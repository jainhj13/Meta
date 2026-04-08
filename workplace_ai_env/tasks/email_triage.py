"""
Email Triage Task — Classify emails and assign priority scores.

Task 1 (Easy): Agent receives 5 emails and must classify each as
urgent/normal/spam and assign a priority score (0-1).
"""

from __future__ import annotations

from typing import Any

from workplace_ai_env.tasks.base_task import BaseTask


class EmailTriageTask(BaseTask):
    """
    Email triage task engine.

    The agent sees email metadata (subject, sender, snippet) but NOT
    the ground truth labels. It must classify each email and score it.
    """

    def __init__(self, scenario: dict):
        super().__init__(scenario)
        self.emails = scenario["emails"]
        self.classified: dict[str, dict] = {}
        self.current_email_idx = 0
        self.task_state = {
            "classified_count": 0,
            "total_emails": len(self.emails),
            "classified": {},
        }

    def get_max_steps(self) -> int:
        return len(self.emails)

    def get_initial_observation(self) -> dict:
        """Return all emails (without ground truth) for classification."""
        return {
            "emails": [
                {
                    "id": e["id"],
                    "from": e["from"],
                    "subject": e["subject"],
                    "body_snippet": e["body_snippet"][:200],
                    "timestamp": e["timestamp"],
                    "has_attachment": e.get("has_attachment", False),
                }
                for e in self.emails
            ],
            "instructions": (
                "Classify each email as 'urgent', 'normal', or 'spam'. "
                "Assign a priority score between 0.0 (lowest) and 1.0 (highest). "
                "Use action_type='classify_email' for each email."
            ),
        }

    def get_available_actions(self) -> list[str]:
        if self.current_email_idx < len(self.emails):
            return ["classify_email"]
        return []

    def execute_action(self, action_type: str, payload: dict) -> dict:
        """
        Process a classify_email action.

        Expected payload:
            email_id: str
            category: "urgent" | "normal" | "spam"
            priority: float (0-1)
        """
        if action_type != "classify_email":
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Invalid action '{action_type}'. Use 'classify_email'.",
                "done": False,
            }

        email_id = payload.get("email_id", "")
        category = payload.get("category", "").lower().strip()
        priority = payload.get("priority", 0.0)

        # Validate
        valid_categories = {"urgent", "normal", "spam"}
        if category not in valid_categories:
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Invalid category '{category}'. Must be one of {valid_categories}.",
                "done": False,
            }

        if not (0.0 <= priority <= 1.0):
            priority = max(0.0, min(1.0, priority))

        # Check email exists
        valid_ids = {e["id"] for e in self.emails}
        if email_id not in valid_ids:
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Unknown email_id '{email_id}'. Valid: {valid_ids}",
                "done": False,
            }

        # Record classification
        self.classified[email_id] = {
            "category": category,
            "priority": priority,
        }
        self.current_email_idx += 1
        self.task_state["classified_count"] = len(self.classified)
        self.task_state["classified"] = dict(self.classified)
        self.current_step += 1

        done = len(self.classified) >= len(self.emails)

        remaining = [
            e["id"] for e in self.emails if e["id"] not in self.classified
        ]

        return {
            "observation": {
                **self.get_initial_observation(),
                "classified_so_far": list(self.classified.keys()),
                "remaining": remaining,
            },
            "is_valid": True,
            "feedback": f"Email '{email_id}' classified as '{category}' with priority {priority:.2f}. "
                        f"({len(self.classified)}/{len(self.emails)} done)",
            "done": done,
        }

    def get_visible_data(self) -> dict:
        """Current view including what's been classified."""
        data = self.get_initial_observation()
        data["classified_so_far"] = list(self.classified.keys())
        data["remaining"] = [
            e["id"] for e in self.emails if e["id"] not in self.classified
        ]
        return data
