"""
WorkplaceEnvironment — Main OpenEnv-compliant environment.

Implements the core reset(), step(), and state() API.
Orchestrates task engines, graders, and reward shaping.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from workplace_ai_env.graders.email_grader import EmailGrader
from workplace_ai_env.graders.scheduling_grader import SchedulingGrader
from workplace_ai_env.graders.workflow_grader import WorkflowGrader
from workplace_ai_env.models import (
    StepResult,
    WorkplaceAction,
    WorkplaceObservation,
    WorkplaceState,
)
from workplace_ai_env.rewards.reward_shaper import RewardShaper
from workplace_ai_env.scenarios.scenario_generator import get_scenario
from workplace_ai_env.tasks.email_triage import EmailTriageTask
from workplace_ai_env.tasks.meeting_scheduler import MeetingSchedulerTask
from workplace_ai_env.tasks.workflow_executor import WorkflowExecutorTask


class WorkplaceEnvironment:
    """
    Main environment class implementing OpenEnv's Gymnasium-style API.

    Manages task lifecycle, grading, and reward shaping. The agent
    interacts through structured actions and receives partial observations.
    """

    TASK_CLASSES = {
        "email_triage": EmailTriageTask,
        "meeting_scheduler": MeetingSchedulerTask,
        "workflow_executor": WorkflowExecutorTask,
    }

    GRADER_CLASSES = {
        "email_triage": EmailGrader,
        "meeting_scheduler": SchedulingGrader,
        "workflow_executor": WorkflowGrader,
    }

    def __init__(self):
        self._state = WorkplaceState()
        self._task = None
        self._grader = None
        self._reward_shaper = RewardShaper()
        self._is_initialized = False

    def reset(
        self,
        task_name: str = "email_triage",
        seed: int = 0,
        episode_id: Optional[str] = None,
    ) -> WorkplaceObservation:
        """
        Initialize a new episode for the given task.

        Args:
            task_name: One of 'email_triage', 'meeting_scheduler', 'workflow_executor'
            seed: Deterministic seed for scenario selection
            episode_id: Optional custom episode ID

        Returns:
            Initial observation (partial view of the environment)
        """
        if task_name not in self.TASK_CLASSES:
            raise ValueError(
                f"Unknown task: {task_name}. "
                f"Valid: {list(self.TASK_CLASSES.keys())}"
            )

        # Load scenario
        scenario = get_scenario(task_name, seed)

        # Initialize task engine
        task_cls = self.TASK_CLASSES[task_name]
        self._task = task_cls(scenario)

        # Initialize grader
        grader_cls = self.GRADER_CLASSES[task_name]
        self._grader = grader_cls()

        # Initialize state
        self._state = WorkplaceState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_name=task_name,
            scenario_id=scenario["id"],
            seed=seed,
            ground_truth=scenario["ground_truth"],
            max_steps=self._task.get_max_steps(),
            done=False,
        )

        self._is_initialized = True

        # Build initial observation
        visible = self._task.get_initial_observation()
        available = self._task.get_available_actions()

        return WorkplaceObservation(
            task_name=task_name,
            step_number=0,
            max_steps=self._state.max_steps,
            visible_data=visible,
            available_actions=available,
            feedback="Environment reset. Ready for actions.",
            done=False,
            reward=0.0,
            metadata={
                "episode_id": self._state.episode_id,
                "scenario_id": self._state.scenario_id,
            },
        )

    def step(self, action: WorkplaceAction) -> StepResult:
        """
        Execute one action in the environment.

        Args:
            action: Structured WorkplaceAction with task_name, action_type, payload

        Returns:
            StepResult containing observation, reward, done flag, and info
        """
        if not self._is_initialized:
            return StepResult(
                observation=WorkplaceObservation(
                    task_name="",
                    feedback="Environment not initialized. Call reset() first.",
                    done=True,
                ),
                reward=-1.0,
                done=True,
                info={"error": "Not initialized"},
            )

        if self._state.done:
            return StepResult(
                observation=WorkplaceObservation(
                    task_name=self._state.task_name,
                    step_number=self._state.step_count,
                    max_steps=self._state.max_steps,
                    feedback="Episode already done.",
                    done=True,
                ),
                reward=0.0,
                done=True,
                info={"error": "Episode already done"},
            )

        # Check step limit
        if self._state.step_count >= self._state.max_steps:
            self._state.done = True
            return StepResult(
                observation=WorkplaceObservation(
                    task_name=self._state.task_name,
                    step_number=self._state.step_count,
                    max_steps=self._state.max_steps,
                    feedback="Maximum steps reached. Episode ended.",
                    done=True,
                ),
                reward=0.0,
                done=True,
                info={"error": "Max steps exceeded"},
            )

        # Increment step
        self._state.step_count += 1

        # Execute action through task engine
        result = self._task.execute_action(action.action_type, action.payload)

        # Record action
        self._state.actions_taken.append({
            "step": self._state.step_count,
            "action_type": action.action_type,
            "payload": action.payload,
            "is_valid": result["is_valid"],
        })

        # Grade the action
        grade = self._grader.grade(
            action_type=action.action_type,
            payload=action.payload,
            ground_truth=self._state.ground_truth,
            task_state=self._task.task_state,
        )

        # Shape reward
        done = result.get("done", False)
        if self._state.step_count >= self._state.max_steps and not done:
            done = True

        reward = self._reward_shaper.shape(
            grade_result=grade,
            task_name=self._state.task_name,
            step_number=self._state.step_count,
            max_steps=self._state.max_steps,
            is_done=done,
            total_steps_used=self._state.step_count,
        )

        # Update state
        self._state.partial_scores.append(grade.score)
        self._state.total_reward += reward
        self._state.done = done
        self._state.task_state = self._task.task_state

        # Build observation
        visible = result.get("observation", self._task.get_visible_data())
        available = self._task.get_available_actions() if not done else []

        observation = WorkplaceObservation(
            task_name=self._state.task_name,
            step_number=self._state.step_count,
            max_steps=self._state.max_steps,
            visible_data=visible,
            available_actions=available,
            feedback=result.get("feedback", ""),
            done=done,
            reward=reward,
            metadata={
                "episode_id": self._state.episode_id,
                "grade_feedback": grade.feedback,
                "grade_score": grade.score,
            },
        )

        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
            info={
                "grade": grade.breakdown,
                "total_reward": self._state.total_reward,
                "steps_used": self._state.step_count,
            },
        )

    @property
    def state(self) -> WorkplaceState:
        """
        Get the full internal state.

        Note: In a real deployment, this would be protected.
        The agent only sees WorkplaceObservation (partial view).
        """
        return self._state
