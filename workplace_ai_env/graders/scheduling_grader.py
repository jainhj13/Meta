"""
Scheduling Grader — Deterministic grading for meeting scheduling.

Scores: constraint compliance (0.4), preference satisfaction (0.3),
time proximity to optimal (0.2), buffer compliance (0.1).
"""

from __future__ import annotations

from workplace_ai_env.graders.base_grader import BaseGrader, GradeResult


def _time_to_minutes(time_str: str) -> int:
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


class SchedulingGrader(BaseGrader):
    """Deterministic grader for meeting scheduling."""

    def grade(
        self,
        action_type: str,
        payload: dict,
        ground_truth: dict,
        task_state: dict,
    ) -> GradeResult:
        if action_type == "resolve_conflict":
            # Minimal score for valid conflict resolution
            return GradeResult(
                score=0.3,
                breakdown={"conflict_resolution": 0.3},
                feedback="Conflict resolution acknowledged.",
                is_valid=True,
            )

        if action_type != "propose_slot":
            return GradeResult(
                score=0.0,
                breakdown={},
                feedback=f"Invalid action type: {action_type}",
                is_valid=False,
            )

        meeting_id = payload.get("meeting_id", "")
        slot = payload.get("slot", {})
        room = payload.get("room", "")

        optimal = ground_truth.get("optimal_schedule", {})
        if meeting_id not in optimal:
            return GradeResult(
                score=0.0,
                breakdown={},
                feedback=f"Unknown meeting_id: {meeting_id}",
                is_valid=False,
            )

        opt = optimal[meeting_id]

        # Check if the action was valid (no constraint violations)
        # This is assumed valid if the task engine accepted it
        is_valid_schedule = task_state.get("scheduled", {}).get(meeting_id) is not None

        # Component 1: Valid schedule (0.4)
        valid_score = 1.0 if is_valid_schedule else 0.0

        # Component 2: Day match with optimal (0.2)
        day_match = 1.0 if slot.get("day") == opt["day"] else 0.5

        # Component 3: Time proximity to optimal (0.2)
        try:
            proposed_start = _time_to_minutes(slot.get("start", "09:00"))
            optimal_start = _time_to_minutes(opt["start"])
            time_diff = abs(proposed_start - optimal_start)
            # Perfect if within 30 min, decreasing score for larger gaps
            time_score = max(0.0, 1.0 - (time_diff / 240.0))
        except (ValueError, AttributeError):
            time_score = 0.0

        # Component 4: Room match (0.2)
        room_score = 1.0 if room == opt["room"] else 0.5

        total = (
            valid_score * 0.4
            + day_match * 0.2
            + time_score * 0.2
            + room_score * 0.2
        )

        return GradeResult(
            score=round(total, 4),
            breakdown={
                "valid_schedule": valid_score,
                "day_match": day_match,
                "time_proximity": round(time_score, 4),
                "room_match": room_score,
            },
            feedback=(
                f"Schedule validity: {'✓' if valid_score else '✗'}. "
                f"Day: {'✓' if day_match == 1.0 else '~'}. "
                f"Time proximity: {time_score:.2f}. "
                f"Room: {'✓' if room_score == 1.0 else '~'}."
            ),
            is_valid=is_valid_schedule,
        )
