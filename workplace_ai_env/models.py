"""
WorkplaceAIEnv++ — Core Pydantic Models

Defines Action, Observation, and State models for the OpenEnv-compliant
workplace decision intelligence environment.

All models use Pydantic BaseModel for type safety, serialization,
and OpenEnv compatibility.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class TaskName(str, Enum):
    """Available tasks in the environment."""
    EMAIL_TRIAGE = "email_triage"
    MEETING_SCHEDULER = "meeting_scheduler"
    WORKFLOW_EXECUTOR = "workflow_executor"


class EmailCategory(str, Enum):
    """Email classification categories."""
    URGENT = "urgent"
    NORMAL = "normal"
    SPAM = "spam"


class ActionType(str, Enum):
    """All valid action types across tasks."""
    # Task 1: Email Triage
    CLASSIFY_EMAIL = "classify_email"

    # Task 2: Meeting Scheduler
    PROPOSE_SLOT = "propose_slot"
    RESOLVE_CONFLICT = "resolve_conflict"

    # Task 3: Workflow Executor
    EXTRACT_TASKS = "extract_tasks"
    ASSIGN_TASK = "assign_task"
    COMPOSE_RESPONSE = "compose_response"


# =============================================================================
# Action Model
# =============================================================================

class WorkplaceAction(BaseModel):
    """
    Structured action for all workplace tasks.

    The agent must produce specific JSON with task_name, action_type,
    and a payload dict containing task-specific parameters.
    """
    task_name: str = Field(
        ...,
        description="Task identifier: email_triage | meeting_scheduler | workflow_executor"
    )
    action_type: str = Field(
        ...,
        description="Action type specific to the current task"
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured parameters for the action"
    )


# =============================================================================
# Observation Model
# =============================================================================

class WorkplaceObservation(BaseModel):
    """
    What the agent can see — intentionally incomplete (partial observability).

    The agent never sees ground truth, full email bodies, or optimal solutions.
    Only filtered, partial information is exposed via visible_data.
    """
    task_name: str = Field(
        ...,
        description="Current task identifier"
    )
    step_number: int = Field(
        default=0,
        description="Current step in this episode"
    )
    max_steps: int = Field(
        default=10,
        description="Maximum steps allowed for this task"
    )
    visible_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Task-specific partial view of the environment state"
    )
    available_actions: list[str] = Field(
        default_factory=list,
        description="Action types valid at this point"
    )
    feedback: str = Field(
        default="",
        description="Result/feedback from the last action taken"
    )
    done: bool = Field(
        default=False,
        description="Whether the episode is complete"
    )
    reward: float = Field(
        default=0.0,
        description="Reward from the last action"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context and status information"
    )


# =============================================================================
# State Model (Internal — NOT exposed to agent)
# =============================================================================

class WorkplaceState(BaseModel):
    """
    Full internal environment state.

    Contains ground truth and scoring data. This is used by the graders
    and reward shaper but is NOT sent to the agent. The agent only sees
    WorkplaceObservation (partial view).
    """
    # OpenEnv required fields
    episode_id: str = Field(
        default="",
        description="Unique identifier for this episode"
    )
    step_count: int = Field(
        default=0,
        description="Number of steps taken so far"
    )

    # Task tracking
    task_name: str = Field(
        default="",
        description="Current task identifier"
    )
    scenario_id: str = Field(
        default="",
        description="ID of the loaded scenario"
    )
    seed: int = Field(
        default=0,
        description="Random seed for reproducibility"
    )

    # Ground truth (hidden from agent)
    ground_truth: dict[str, Any] = Field(
        default_factory=dict,
        description="Correct answers for deterministic grading"
    )

    # Progress tracking
    actions_taken: list[dict[str, Any]] = Field(
        default_factory=list,
        description="History of all actions in this episode"
    )
    partial_scores: list[float] = Field(
        default_factory=list,
        description="Score achieved per action"
    )
    total_reward: float = Field(
        default=0.0,
        description="Cumulative reward in this episode"
    )
    max_steps: int = Field(
        default=10,
        description="Maximum steps for this task"
    )

    # Task-specific internal state
    task_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Internal task data (calendar state, assigned tasks, etc.)"
    )

    # Episode status
    done: bool = Field(
        default=False,
        description="Whether episode is finished"
    )


# =============================================================================
# StepResult — wrapper returned by step()
# =============================================================================

class StepResult(BaseModel):
    """Result of a single step in the environment."""
    observation: WorkplaceObservation
    reward: float = 0.0
    done: bool = False
    info: dict[str, Any] = Field(default_factory=dict)
