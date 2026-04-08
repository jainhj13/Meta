"""
Workflow Executor Task — Multi-step workflow execution.

Task 3 (Hard): Agent must extract tasks from email threads,
prioritize them, assign to team members, and compose a response.
Requires state memory across steps.
"""

from __future__ import annotations

from typing import Any

from workplace_ai_env.tasks.base_task import BaseTask


class WorkflowExecutorTask(BaseTask):
    """
    Multi-step workflow executor.

    Steps:
    1. extract_tasks — Parse email thread and identify action items
    2. assign_task — Assign each task to a team member (repeated)
    3. compose_response — Write a professional response
    """

    STEP_SEQUENCE = ["extract_tasks", "assign_task", "compose_response"]

    def __init__(self, scenario: dict):
        super().__init__(scenario)
        self.email_thread = scenario["email_thread"]
        self.team_members = scenario["team_members"]
        self.task_board = scenario["task_board"]

        self.extracted_tasks: list[dict] = []
        self.assignments: dict[str, dict] = {}
        self.response_composed = False
        self.response_text = ""

        self.phase = "extract_tasks"  # Current phase
        self.assign_count = 0

        self.task_state = {
            "phase": self.phase,
            "extracted_tasks": [],
            "assignments": {},
            "response": "",
        }

    def get_max_steps(self) -> int:
        return 10

    def get_initial_observation(self) -> dict:
        """Return email thread and team info (partial view)."""
        return {
            "email_thread": [
                {
                    "id": msg["id"],
                    "from": msg["from"],
                    "to": msg["to"],
                    "subject": msg["subject"],
                    "body": msg["body"],
                    "timestamp": msg["timestamp"],
                }
                for msg in self.email_thread
            ],
            "team_members": [
                {
                    "name": tm["name"],
                    "role": tm["role"],
                    "current_tasks": tm["current_tasks"],
                    # Skills visible but NOT the ground truth best_assignee
                }
                for tm in self.team_members
            ],
            "task_board": self.task_board,
            "instructions": (
                "Complete this workflow in order:\n"
                "1. extract_tasks: Identify action items from the email thread\n"
                "2. assign_task: Assign each extracted task to a team member\n"
                "3. compose_response: Write a professional response email\n"
            ),
        }

    def get_available_actions(self) -> list[str]:
        if self.phase == "extract_tasks":
            return ["extract_tasks"]
        elif self.phase == "assign_task":
            return ["assign_task"]
        elif self.phase == "compose_response":
            return ["compose_response"]
        return []

    def execute_action(self, action_type: str, payload: dict) -> dict:
        """Route to the appropriate handler based on phase."""
        if action_type == "extract_tasks":
            return self._handle_extract(payload)
        elif action_type == "assign_task":
            return self._handle_assign(payload)
        elif action_type == "compose_response":
            return self._handle_compose(payload)
        else:
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Invalid action '{action_type}'. Current phase: {self.phase}",
                "done": False,
            }

    def _handle_extract(self, payload: dict) -> dict:
        """Extract tasks from email thread."""
        if self.phase != "extract_tasks":
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Wrong phase. Current phase: '{self.phase}', not 'extract_tasks'.",
                "done": False,
            }

        tasks = payload.get("tasks", [])
        if not isinstance(tasks, list) or len(tasks) == 0:
            self.current_step += 1
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": "Payload must include 'tasks': a non-empty list of task objects.",
                "done": False,
            }

        # Store extracted tasks
        self.extracted_tasks = []
        for i, task in enumerate(tasks):
            self.extracted_tasks.append({
                "id": task.get("id", f"task_{i+1:03d}"),
                "description": task.get("description", ""),
                "priority": task.get("priority", 3),
            })

        self.phase = "assign_task"
        self.task_state["phase"] = self.phase
        self.task_state["extracted_tasks"] = list(self.extracted_tasks)
        self.current_step += 1

        return {
            "observation": {
                **self.get_visible_data(),
                "extracted_tasks": self.extracted_tasks,
                "next_step": "Assign each task to a team member using 'assign_task'.",
            },
            "is_valid": True,
            "feedback": f"Extracted {len(self.extracted_tasks)} tasks. Now assign each to a team member.",
            "done": False,
        }

    def _handle_assign(self, payload: dict) -> dict:
        """Assign a task to a team member."""
        if self.phase != "assign_task":
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Wrong phase. Current phase: '{self.phase}', not 'assign_task'.",
                "done": False,
            }

        task_id = payload.get("task_id", "")
        assignee = payload.get("assignee", "").lower().strip()
        deadline = payload.get("deadline", "")

        # Validate team member exists
        valid_members = {tm["name"] for tm in self.team_members}
        if assignee not in valid_members:
            self.current_step += 1
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Unknown assignee '{assignee}'. Valid: {valid_members}",
                "done": False,
            }

        # Record assignment
        self.assignments[task_id] = {
            "assignee": assignee,
            "deadline": deadline,
        }
        self.assign_count += 1
        self.task_state["assignments"] = dict(self.assignments)
        self.current_step += 1

        # Check if all tasks assigned
        all_assigned = len(self.assignments) >= len(self.extracted_tasks)
        if all_assigned:
            self.phase = "compose_response"
            self.task_state["phase"] = self.phase

        unassigned = [
            t["id"] for t in self.extracted_tasks if t["id"] not in self.assignments
        ]

        return {
            "observation": {
                **self.get_visible_data(),
                "assignments_so_far": dict(self.assignments),
                "unassigned_tasks": unassigned,
                "next_step": (
                    "Compose a professional response email."
                    if all_assigned
                    else f"Assign remaining tasks: {unassigned}"
                ),
            },
            "is_valid": True,
            "feedback": (
                f"Task '{task_id}' assigned to '{assignee}' (deadline: {deadline}). "
                f"({len(self.assignments)}/{len(self.extracted_tasks)} assigned)"
            ),
            "done": False,
        }

    def _handle_compose(self, payload: dict) -> dict:
        """Compose a response email."""
        if self.phase != "compose_response":
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Wrong phase. Current phase: '{self.phase}', not 'compose_response'.",
                "done": False,
            }

        response_text = payload.get("response_text", "")
        action_items = payload.get("action_items", [])

        if not response_text or len(response_text.strip()) < 20:
            self.current_step += 1
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": "Response text must be at least 20 characters.",
                "done": False,
            }

        self.response_text = response_text
        self.response_composed = True
        self.task_state["response"] = response_text
        self.current_step += 1

        return {
            "observation": self.get_visible_data(),
            "is_valid": True,
            "feedback": "Response composed successfully. Workflow complete!",
            "done": True,
        }

    def get_visible_data(self) -> dict:
        data = self.get_initial_observation()
        data["current_phase"] = self.phase
        data["extracted_tasks"] = list(self.extracted_tasks)
        data["assignments"] = dict(self.assignments)
        if self.response_composed:
            data["response_composed"] = True
        return data
