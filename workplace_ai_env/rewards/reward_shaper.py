"""
Reward Shaper — Dense reward engineering with partial credit.

Converts GradeResult scores into shaped rewards with bonuses
for task completion and step efficiency.
"""

from __future__ import annotations

from workplace_ai_env.graders.base_grader import GradeResult


class RewardShaper:
    """
    Shapes raw grading scores into meaningful rewards.

    Reward = step_score + completion_bonus + efficiency_bonus
    """

    # Per-task completion bonuses
    COMPLETION_BONUS = {
        "email_triage": 0.5,
        "meeting_scheduler": 0.5,
        "workflow_executor": 1.0,
    }

    def shape(
        self,
        grade_result: GradeResult,
        task_name: str,
        step_number: int,
        max_steps: int,
        is_done: bool,
        total_steps_used: int = 0,
    ) -> float:
        """
        Shape the reward from a grade result.

        Args:
            grade_result: The deterministic grade for this action
            task_name: Current task name
            step_number: Current step number
            max_steps: Maximum steps allowed
            is_done: Whether the episode is complete
            total_steps_used: Total steps used when done

        Returns:
            Shaped reward value
        """
        if not grade_result.is_valid:
            # Invalid actions get a small negative reward
            return -0.1

        # Base score from grader
        reward = grade_result.score

        # Completion bonus
        if is_done:
            bonus = self.COMPLETION_BONUS.get(task_name, 0.0)
            reward += bonus

            # Efficiency bonus: reward finishing in fewer steps
            if total_steps_used > 0 and max_steps > 0:
                efficiency = max(0.0, (max_steps - total_steps_used) / max_steps)
                reward += efficiency * 0.2

        return round(reward, 4)
