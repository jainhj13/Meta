"""
Base Task — Abstract interface for all task engines.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTask(ABC):
    """Abstract base class for all workplace tasks."""

    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.scenario_id = scenario["id"]
        self.ground_truth = scenario["ground_truth"]
        self.current_step = 0
        self.task_state: dict[str, Any] = {}
        self.actions_history: list[dict] = []

    @abstractmethod
    def get_initial_observation(self) -> dict:
        """Return the initial partial observation for this task."""
        pass

    @abstractmethod
    def get_available_actions(self) -> list[str]:
        """Return action types valid at the current step."""
        pass

    @abstractmethod
    def execute_action(self, action_type: str, payload: dict) -> dict:
        """
        Execute an action and return result.

        Returns:
            dict with keys: observation, is_valid, feedback, done
        """
        pass

    @abstractmethod
    def get_max_steps(self) -> int:
        """Maximum steps allowed for this task."""
        pass

    def get_visible_data(self) -> dict:
        """Get the current partial view for the agent."""
        return self.get_initial_observation()
