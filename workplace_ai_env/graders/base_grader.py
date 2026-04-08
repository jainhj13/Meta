"""
Base Grader — Abstract interface for deterministic graders.

All graders are pure functions: same input → same output. No randomness. No LLM calls.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GradeResult:
    """Result of grading a single action."""
    score: float = 0.0          # 0.0 to 1.0
    breakdown: dict = field(default_factory=dict)  # Per-component scores
    feedback: str = ""          # Human-readable explanation
    is_valid: bool = True       # Whether the action was structurally valid


class BaseGrader(ABC):
    """Abstract base for all deterministic graders."""

    @abstractmethod
    def grade(
        self,
        action_type: str,
        payload: dict,
        ground_truth: dict,
        task_state: dict,
    ) -> GradeResult:
        """
        Grade a single action deterministically.

        Args:
            action_type: The action type performed
            payload: The action payload
            ground_truth: Hidden correct answers
            task_state: Current internal task state

        Returns:
            GradeResult with score, breakdown, and feedback
        """
        pass
