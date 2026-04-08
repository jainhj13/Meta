"""
Workflow Grader — Deterministic grading for multi-step workflow execution.

Grades each phase: task extraction (precision/recall), assignment quality
(role match, workload), and response quality (keyword presence).
"""

from __future__ import annotations

from workplace_ai_env.graders.base_grader import BaseGrader, GradeResult


class WorkflowGrader(BaseGrader):
    """Deterministic grader for workflow execution."""

    def grade(
        self,
        action_type: str,
        payload: dict,
        ground_truth: dict,
        task_state: dict,
    ) -> GradeResult:
        if action_type == "extract_tasks":
            return self._grade_extraction(payload, ground_truth)
        elif action_type == "assign_task":
            return self._grade_assignment(payload, ground_truth, task_state)
        elif action_type == "compose_response":
            return self._grade_response(payload, ground_truth, task_state)
        else:
            return GradeResult(
                score=0.0,
                breakdown={},
                feedback=f"Invalid action type: {action_type}",
                is_valid=False,
            )

    def _grade_extraction(self, payload: dict, ground_truth: dict) -> GradeResult:
        """Grade task extraction using keyword matching."""
        extracted = payload.get("tasks", [])
        gt_tasks = ground_truth.get("tasks", [])

        if not extracted:
            return GradeResult(
                score=0.0,
                breakdown={"recall": 0.0, "precision": 0.0},
                feedback="No tasks extracted.",
                is_valid=False,
            )

        # Match extracted tasks to ground truth using keyword overlap
        gt_descriptions = [t["description"].lower() for t in gt_tasks]
        extracted_descriptions = [
            t.get("description", "").lower() for t in extracted
        ]

        matches = 0
        for ext_desc in extracted_descriptions:
            ext_words = set(ext_desc.split())
            for gt_desc in gt_descriptions:
                gt_words = set(gt_desc.split())
                # Consider a match if ≥40% word overlap
                if len(ext_words) > 0 and len(gt_words) > 0:
                    overlap = len(ext_words & gt_words) / len(gt_words)
                    if overlap >= 0.4:
                        matches += 1
                        break

        recall = matches / len(gt_tasks) if gt_tasks else 0.0
        precision = matches / len(extracted) if extracted else 0.0

        # Count score (more weight on recall)
        total = (recall * 0.6) + (precision * 0.4)

        return GradeResult(
            score=round(total, 4),
            breakdown={
                "recall": round(recall, 4),
                "precision": round(precision, 4),
                "tasks_found": matches,
                "tasks_expected": len(gt_tasks),
                "tasks_extracted": len(extracted),
            },
            feedback=(
                f"Extraction: {matches}/{len(gt_tasks)} tasks matched. "
                f"Recall={recall:.2f}, Precision={precision:.2f}"
            ),
            is_valid=True,
        )

    def _grade_assignment(
        self, payload: dict, ground_truth: dict, task_state: dict
    ) -> GradeResult:
        """Grade task assignment based on role/skill match."""
        task_id = payload.get("task_id", "")
        assignee = payload.get("assignee", "").lower().strip()

        gt_tasks = ground_truth.get("tasks", [])
        gt_task = None
        for t in gt_tasks:
            if t["id"] == task_id:
                gt_task = t
                break

        if not gt_task:
            # Try matching by index if IDs don't match
            assignments = task_state.get("assignments", {})
            idx = len(assignments) - 1
            if 0 <= idx < len(gt_tasks):
                gt_task = gt_tasks[idx]

        if not gt_task:
            return GradeResult(
                score=0.3,  # Partial credit for attempting
                breakdown={"assignee_match": 0.0, "attempt": 1.0},
                feedback=f"Task '{task_id}' not in ground truth, partial credit given.",
                is_valid=True,
            )

        # Check assignee match
        best_assignee = gt_task.get("best_assignee", "")
        assignee_score = 1.0 if assignee == best_assignee else 0.3

        return GradeResult(
            score=round(assignee_score, 4),
            breakdown={
                "assignee_match": assignee_score,
                "expected_assignee": best_assignee,
                "actual_assignee": assignee,
            },
            feedback=(
                f"Assignment: {'✓ Optimal' if assignee_score == 1.0 else '~ Suboptimal'} "
                f"(assigned={assignee}, optimal={best_assignee})"
            ),
            is_valid=True,
        )

    def _grade_response(
        self, payload: dict, ground_truth: dict, task_state: dict
    ) -> GradeResult:
        """Grade response quality using keyword presence checks."""
        response_text = payload.get("response_text", "").lower()

        if len(response_text.strip()) < 20:
            return GradeResult(
                score=0.0,
                breakdown={},
                feedback="Response too short.",
                is_valid=False,
            )

        must_include = ground_truth.get("response_must_include", [])

        # Keyword-based checks (deterministic, no LLM)
        keyword_map = {
            "acknowledge deliverables": ["deliverable", "request", "noted", "acknowledge", "received"],
            "mention timeline": ["friday", "deadline", "by", "week", "timeline", "due"],
            "reference login bug fix": ["login", "bug", "fix", "issue", "resolve"],
            "provide assignee names": [],  # Check dynamically
            "acknowledge Q4 launch": ["q4", "launch", "quarter", "release"],
            "mention database migration priority": ["database", "migration", "priority", "postgresql", "postgres"],
            "provide timeline": ["week", "deadline", "timeline", "by", "days"],
            "reference team assignments": ["assign", "team", "responsible", "task"],
            "acknowledge security alert": ["security", "alert", "vulnerability", "critical", "urgent"],
            "mention 24-hour deadline": ["24", "hour", "immediate", "asap", "urgent"],
            "reference SQL injection fix": ["sql", "injection", "fix", "patch", "security"],
            "mention TLS certificate update": ["tls", "certificate", "ssl", "update", "renew"],
            "provide status update plan": ["status", "update", "hourly", "progress", "report"],
        }

        # Get team member names from task state
        assignments = task_state.get("assignments", {})
        assignee_names = set()
        for a in assignments.values():
            if isinstance(a, dict):
                assignee_names.add(a.get("assignee", ""))

        hits = 0
        details = {}
        for requirement in must_include:
            keywords = keyword_map.get(requirement, [])

            if requirement == "provide assignee names":
                # Check if any assignee name appears in response
                found = any(name in response_text for name in assignee_names if name)
                details[requirement] = found
                if found:
                    hits += 1
            elif keywords:
                found = any(kw in response_text for kw in keywords)
                details[requirement] = found
                if found:
                    hits += 1
            else:
                # No keywords defined — give credit
                hits += 1
                details[requirement] = True

        score = hits / len(must_include) if must_include else 0.5

        return GradeResult(
            score=round(score, 4),
            breakdown={
                "requirements_met": hits,
                "requirements_total": len(must_include),
                "details": details,
            },
            feedback=(
                f"Response quality: {hits}/{len(must_include)} requirements met. "
                f"Score: {score:.2f}"
            ),
            is_valid=True,
        )
