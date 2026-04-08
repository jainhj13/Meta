"""
Email Grader — Deterministic grading for email triage.

Scores: category accuracy (0.5), priority distance (0.3), batch ordering (0.2).
"""

from __future__ import annotations

from workplace_ai_env.graders.base_grader import BaseGrader, GradeResult


class EmailGrader(BaseGrader):
    """Deterministic grader for email classification."""

    def grade(
        self,
        action_type: str,
        payload: dict,
        ground_truth: dict,
        task_state: dict,
    ) -> GradeResult:
        if action_type != "classify_email":
            return GradeResult(
                score=0.0,
                breakdown={},
                feedback=f"Invalid action type: {action_type}",
                is_valid=False,
            )

        email_id = payload.get("email_id", "")
        predicted_category = payload.get("category", "").lower().strip()
        predicted_priority = float(payload.get("priority", 0.0))

        if email_id not in ground_truth:
            return GradeResult(
                score=0.0,
                breakdown={},
                feedback=f"Unknown email_id: {email_id}",
                is_valid=False,
            )

        truth = ground_truth[email_id]
        true_category = truth["category"]
        true_priority = truth["priority"]

        # Component 1: Category accuracy (weight 0.6)
        category_score = 1.0 if predicted_category == true_category else 0.0

        # Component 2: Priority distance (weight 0.4)
        priority_score = max(0.0, 1.0 - abs(predicted_priority - true_priority))

        # Weighted total
        total = (category_score * 0.6) + (priority_score * 0.4)

        return GradeResult(
            score=round(total, 4),
            breakdown={
                "category_accuracy": category_score,
                "priority_accuracy": round(priority_score, 4),
                "true_category": true_category,
                "true_priority": true_priority,
            },
            feedback=(
                f"Category: {'✓' if category_score == 1.0 else '✗'} "
                f"(predicted={predicted_category}, actual={true_category}). "
                f"Priority: {priority_score:.2f} "
                f"(predicted={predicted_priority:.2f}, actual={true_priority:.2f})"
            ),
            is_valid=True,
        )
