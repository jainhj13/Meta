"""
Integration tests for WorkplaceAIEnv++.

Tests every component: environment lifecycle, all 3 tasks,
graders, rewards, and the FastAPI server.
"""

from __future__ import annotations

import pytest

from workplace_ai_env.graders.email_grader import EmailGrader
from workplace_ai_env.graders.scheduling_grader import SchedulingGrader
from workplace_ai_env.graders.workflow_grader import WorkflowGrader
from workplace_ai_env.models import WorkplaceAction
from workplace_ai_env.rewards.reward_shaper import RewardShaper
from workplace_ai_env.server.workplace_environment import WorkplaceEnvironment


# =============================================================================
# Environment Lifecycle Tests
# =============================================================================

class TestEnvironmentLifecycle:
    """Test basic environment operations."""

    def test_reset_returns_observation(self):
        env = WorkplaceEnvironment()
        obs = env.reset(task_name="email_triage", seed=0)
        assert obs.task_name == "email_triage"
        assert obs.step_number == 0
        assert obs.done is False
        assert len(obs.visible_data) > 0
        assert len(obs.available_actions) > 0

    def test_reset_all_tasks(self):
        env = WorkplaceEnvironment()
        for task in ["email_triage", "meeting_scheduler", "workflow_executor"]:
            obs = env.reset(task_name=task, seed=0)
            assert obs.task_name == task
            assert obs.done is False

    def test_invalid_task_raises(self):
        env = WorkplaceEnvironment()
        with pytest.raises(ValueError):
            env.reset(task_name="nonexistent")

    def test_step_without_reset_returns_error(self):
        env = WorkplaceEnvironment()
        action = WorkplaceAction(
            task_name="email_triage",
            action_type="classify_email",
            payload={},
        )
        result = env.step(action)
        assert result.done is True
        assert result.reward == -1.0

    def test_state_tracks_steps(self):
        env = WorkplaceEnvironment()
        env.reset(task_name="email_triage", seed=0)
        assert env.state.step_count == 0

        action = WorkplaceAction(
            task_name="email_triage",
            action_type="classify_email",
            payload={
                "email_id": "email_001",
                "category": "urgent",
                "priority": 0.9,
            },
        )
        env.step(action)
        assert env.state.step_count == 1


# =============================================================================
# Email Triage Tests
# =============================================================================

class TestEmailTriage:
    """Test email triage task end-to-end."""

    def test_full_episode(self):
        env = WorkplaceEnvironment()
        obs = env.reset(task_name="email_triage", seed=0)

        emails = obs.visible_data["emails"]
        assert len(emails) == 5

        # Classify all 5 emails with known correct answers
        correct_answers = {
            "email_001": ("urgent", 0.92),
            "email_002": ("spam", 0.05),
            "email_003": ("normal", 0.35),
            "email_004": ("urgent", 0.98),
            "email_005": ("normal", 0.45),
        }

        for email_id, (category, priority) in correct_answers.items():
            action = WorkplaceAction(
                task_name="email_triage",
                action_type="classify_email",
                payload={
                    "email_id": email_id,
                    "category": category,
                    "priority": priority,
                },
            )
            result = env.step(action)
            assert result.reward > 0, f"Correct answer should get positive reward for {email_id}"

        # Last step should be done
        assert result.done is True

    def test_wrong_category_gets_lower_score(self):
        env = WorkplaceEnvironment()
        env.reset(task_name="email_triage", seed=0)

        # Wrong category for email_001 (should be urgent)
        action = WorkplaceAction(
            task_name="email_triage",
            action_type="classify_email",
            payload={
                "email_id": "email_001",
                "category": "spam",
                "priority": 0.92,
            },
        )
        wrong_result = env.step(action)

        env.reset(task_name="email_triage", seed=0)
        # Correct category
        action2 = WorkplaceAction(
            task_name="email_triage",
            action_type="classify_email",
            payload={
                "email_id": "email_001",
                "category": "urgent",
                "priority": 0.92,
            },
        )
        correct_result = env.step(action2)

        assert correct_result.reward > wrong_result.reward


# =============================================================================
# Meeting Scheduler Tests
# =============================================================================

class TestMeetingScheduler:
    """Test meeting scheduler task."""

    def test_valid_scheduling(self):
        env = WorkplaceEnvironment()
        obs = env.reset(task_name="meeting_scheduler", seed=0)

        assert len(obs.visible_data["meetings"]) == 3

        # Schedule meeting 1
        action = WorkplaceAction(
            task_name="meeting_scheduler",
            action_type="propose_slot",
            payload={
                "meeting_id": "mtg_001",
                "slot": {"day": "Mon", "start": "10:00", "end": "11:00"},
                "room": "room_a",
            },
        )
        result = env.step(action)
        assert result.reward > 0

    def test_constraint_violation_detected(self):
        env = WorkplaceEnvironment()
        env.reset(task_name="meeting_scheduler", seed=0)

        # Try to schedule during blocked time for alice (Mon 09:00-10:00)
        action = WorkplaceAction(
            task_name="meeting_scheduler",
            action_type="propose_slot",
            payload={
                "meeting_id": "mtg_001",
                "slot": {"day": "Mon", "start": "09:00", "end": "10:00"},
                "room": "room_a",
            },
        )
        result = env.step(action)
        # Should get negative reward for constraint violation
        assert result.reward <= 0


# =============================================================================
# Workflow Executor Tests
# =============================================================================

class TestWorkflowExecutor:
    """Test workflow executor task."""

    def test_full_workflow(self):
        env = WorkplaceEnvironment()
        obs = env.reset(task_name="workflow_executor", seed=0)

        assert "email_thread" in obs.visible_data

        # Step 1: Extract tasks
        action = WorkplaceAction(
            task_name="workflow_executor",
            action_type="extract_tasks",
            payload={
                "tasks": [
                    {"id": "task_001", "description": "Update wireframes for mobile app", "priority": 2},
                    {"id": "task_002", "description": "Write API documentation for payment integration", "priority": 3},
                    {"id": "task_003", "description": "Run performance tests on staging", "priority": 3},
                    {"id": "task_004", "description": "Fix login bug", "priority": 1},
                ]
            },
        )
        result = env.step(action)
        assert result.reward > 0
        assert result.done is False

        # Step 2-5: Assign tasks
        assignments = [
            ("task_001", "bob", "Friday"),
            ("task_002", "alice", "Friday"),
            ("task_003", "charlie", "Friday"),
            ("task_004", "diana", "ASAP"),
        ]

        for task_id, assignee, deadline in assignments:
            action = WorkplaceAction(
                task_name="workflow_executor",
                action_type="assign_task",
                payload={
                    "task_id": task_id,
                    "assignee": assignee,
                    "deadline": deadline,
                },
            )
            result = env.step(action)
            assert result.reward > 0

        # Step 6: Compose response
        action = WorkplaceAction(
            task_name="workflow_executor",
            action_type="compose_response",
            payload={
                "response_text": (
                    "Hi Jameson, thank you for the deliverables request. "
                    "We have noted all items and will have them ready by Friday. "
                    "The login bug fix has been prioritized and assigned to Diana for ASAP resolution. "
                    "Bob will handle the wireframes, Alice the API documentation, "
                    "and Charlie the performance tests. "
                    "We will provide a status update by end of day."
                ),
                "action_items": [
                    "Fix login bug (Diana - ASAP)",
                    "Update wireframes (Bob - Friday)",
                    "API docs (Alice - Friday)",
                    "Performance tests (Charlie - Friday)",
                ],
            },
        )
        result = env.step(action)
        assert result.done is True
        assert result.reward > 0


# =============================================================================
# Grader Determinism Tests
# =============================================================================

class TestGraderDeterminism:
    """Verify graders produce identical output for identical input."""

    def test_email_grader_deterministic(self):
        grader = EmailGrader()
        gt = {"email_001": {"category": "urgent", "priority": 0.92}}

        r1 = grader.grade("classify_email", {"email_id": "email_001", "category": "urgent", "priority": 0.9}, gt, {})
        r2 = grader.grade("classify_email", {"email_id": "email_001", "category": "urgent", "priority": 0.9}, gt, {})

        assert r1.score == r2.score
        assert r1.breakdown == r2.breakdown

    def test_scheduling_grader_deterministic(self):
        grader = SchedulingGrader()
        gt = {
            "optimal_schedule": {
                "mtg_001": {"day": "Mon", "start": "10:00", "end": "11:00", "room": "room_a"}
            }
        }
        payload = {"meeting_id": "mtg_001", "slot": {"day": "Mon", "start": "10:00"}, "room": "room_a"}
        state = {"scheduled": {"mtg_001": True}}

        r1 = grader.grade("propose_slot", payload, gt, state)
        r2 = grader.grade("propose_slot", payload, gt, state)

        assert r1.score == r2.score

    def test_workflow_grader_deterministic(self):
        grader = WorkflowGrader()
        gt = {
            "tasks": [
                {"id": "t1", "description": "Fix the login bug", "priority": 1, "best_assignee": "alice"}
            ],
            "response_must_include": ["mention timeline"],
        }

        payload = {"tasks": [{"id": "t1", "description": "Fix the login bug", "priority": 1}]}
        r1 = grader.grade("extract_tasks", payload, gt, {})
        r2 = grader.grade("extract_tasks", payload, gt, {})

        assert r1.score == r2.score


# =============================================================================
# Reward Shaper Tests
# =============================================================================

class TestRewardShaper:
    """Test reward shaping logic."""

    def test_invalid_action_negative_reward(self):
        from workplace_ai_env.graders.base_grader import GradeResult

        shaper = RewardShaper()
        grade = GradeResult(score=0.0, is_valid=False)
        reward = shaper.shape(grade, "email_triage", 1, 5, False)
        assert reward == -0.1

    def test_completion_bonus(self):
        from workplace_ai_env.graders.base_grader import GradeResult

        shaper = RewardShaper()
        grade = GradeResult(score=0.8, is_valid=True)

        # Without completion
        r1 = shaper.shape(grade, "email_triage", 1, 5, is_done=False)
        # With completion
        r2 = shaper.shape(grade, "email_triage", 5, 5, is_done=True, total_steps_used=5)

        assert r2 > r1  # Completion bonus should make it higher

    def test_efficiency_bonus(self):
        from workplace_ai_env.graders.base_grader import GradeResult

        shaper = RewardShaper()
        grade = GradeResult(score=1.0, is_valid=True)

        # Finish in fewer steps = higher efficiency bonus
        r_fast = shaper.shape(grade, "email_triage", 3, 10, is_done=True, total_steps_used=3)
        r_slow = shaper.shape(grade, "email_triage", 9, 10, is_done=True, total_steps_used=9)

        assert r_fast > r_slow


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
