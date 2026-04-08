"""
Meeting Scheduler Task — Constraint-based meeting scheduling.

Task 2 (Medium): Agent must schedule 3 meetings into a weekly calendar
respecting hard constraints (no overlap, room capacity, blocked hours,
30-minute buffers between meetings for same participants).
"""

from __future__ import annotations

from typing import Any

from workplace_ai_env.tasks.base_task import BaseTask


def _time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' to minutes since midnight."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to 'HH:MM'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class MeetingSchedulerTask(BaseTask):
    """
    Meeting scheduler task engine.

    The agent sees participant availability (with some gaps), room list,
    and meeting requirements. It must propose valid time slots.
    """

    def __init__(self, scenario: dict):
        super().__init__(scenario)
        self.meetings = scenario["meetings"]
        self.participants = scenario["participants"]
        self.rooms = scenario["rooms"]
        self.work_hours = scenario["work_hours"]
        self.scheduled: dict[str, dict] = {}
        self.meeting_idx = 0
        self.task_state = {
            "scheduled": {},
            "conflicts": [],
            "calendar": {},
        }

    def get_max_steps(self) -> int:
        return 8  # 3 meetings + potential conflict resolutions

    def get_initial_observation(self) -> dict:
        """Return meeting requirements and constraints (partial view)."""
        return {
            "meetings": [
                {
                    "id": m["id"],
                    "title": m["title"],
                    "duration_minutes": m["duration_minutes"],
                    "participants": m["participants"],
                    "priority": m["priority"],
                    "preferred_time": m["preferred_time"],
                }
                for m in self.meetings
            ],
            "participant_availability": {
                name: {"blocked_slots": info["blocked"]}
                for name, info in self.participants.items()
            },
            "rooms": self.rooms,
            "work_hours": self.work_hours,
            "rules": [
                "No time overlap for the same participant",
                "Room capacity must accommodate all participants",
                "Respect blocked hours for each participant",
                "30-minute buffer between meetings for the same person",
            ],
            "instructions": (
                "Schedule each meeting by proposing a time slot. "
                "Use action_type='propose_slot' with meeting_id, "
                "slot: {day, start, end}, and room."
            ),
        }

    def get_available_actions(self) -> list[str]:
        if len(self.scheduled) < len(self.meetings):
            return ["propose_slot"]
        if self.task_state.get("conflicts"):
            return ["resolve_conflict"]
        return []

    def _check_constraints(self, meeting_id: str, slot: dict, room: str) -> list[str]:
        """Check all constraints and return list of violations."""
        violations = []
        meeting = next((m for m in self.meetings if m["id"] == meeting_id), None)
        if not meeting:
            violations.append(f"Unknown meeting '{meeting_id}'")
            return violations

        day = slot.get("day", "")
        start = slot.get("start", "09:00")
        end = slot.get("end", "10:00")

        try:
            start_min = _time_to_minutes(start)
            end_min = _time_to_minutes(end)
        except (ValueError, AttributeError):
            violations.append(f"Invalid time format: start={start}, end={end}")
            return violations

        work_start = _time_to_minutes(self.work_hours["start"])
        work_end = _time_to_minutes(self.work_hours["end"])

        # Check work hours
        if start_min < work_start or end_min > work_end:
            violations.append(f"Outside work hours ({self.work_hours['start']}-{self.work_hours['end']})")

        # Check duration matches
        expected_duration = meeting["duration_minutes"]
        actual_duration = end_min - start_min
        if actual_duration != expected_duration:
            violations.append(f"Duration mismatch: expected {expected_duration}min, got {actual_duration}min")

        # Check room capacity
        room_info = next((r for r in self.rooms if r["id"] == room), None)
        if not room_info:
            violations.append(f"Unknown room '{room}'")
        elif len(meeting["participants"]) > room_info["capacity"]:
            violations.append(
                f"Room '{room}' capacity {room_info['capacity']} "
                f"< {len(meeting['participants'])} participants"
            )

        # Check blocked hours
        for participant in meeting["participants"]:
            if participant in self.participants:
                for blocked in self.participants[participant]["blocked"]:
                    if blocked["day"] == day:
                        b_start = _time_to_minutes(blocked["start"])
                        b_end = _time_to_minutes(blocked["end"])
                        if start_min < b_end and end_min > b_start:
                            violations.append(
                                f"Participant '{participant}' blocked on {day} "
                                f"{blocked['start']}-{blocked['end']}"
                            )

        # Check overlap with already scheduled meetings
        for sched_id, sched in self.scheduled.items():
            if sched_id == meeting_id:
                continue
            sched_meeting = next((m for m in self.meetings if m["id"] == sched_id), None)
            if not sched_meeting:
                continue

            if sched["day"] == day:
                s_start = _time_to_minutes(sched["start"])
                s_end = _time_to_minutes(sched["end"])

                # Check room overlap
                if sched["room"] == room and start_min < s_end and end_min > s_start:
                    violations.append(f"Room '{room}' conflict with '{sched_id}'")

                # Check participant overlap + buffer
                common = set(meeting["participants"]) & set(sched_meeting["participants"])
                if common:
                    buffer = 30  # 30-minute buffer
                    if start_min < (s_end + buffer) and end_min > (s_start - buffer):
                        if start_min < s_end and end_min > s_start:
                            violations.append(
                                f"Time overlap for {common} with '{sched_id}'"
                            )
                        else:
                            violations.append(
                                f"Insufficient 30-min buffer for {common} "
                                f"between this and '{sched_id}'"
                            )

        return violations

    def execute_action(self, action_type: str, payload: dict) -> dict:
        """Process propose_slot or resolve_conflict actions."""
        if action_type == "propose_slot":
            return self._handle_propose_slot(payload)
        elif action_type == "resolve_conflict":
            return self._handle_resolve_conflict(payload)
        else:
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Invalid action '{action_type}'. Use 'propose_slot' or 'resolve_conflict'.",
                "done": False,
            }

    def _handle_propose_slot(self, payload: dict) -> dict:
        meeting_id = payload.get("meeting_id", "")
        slot = payload.get("slot", {})
        room = payload.get("room", "")

        violations = self._check_constraints(meeting_id, slot, room)

        if violations:
            self.current_step += 1
            return {
                "observation": self.get_visible_data(),
                "is_valid": False,
                "feedback": f"Constraint violations for '{meeting_id}': {'; '.join(violations)}",
                "done": False,
            }

        # Schedule successfully
        self.scheduled[meeting_id] = {
            "day": slot["day"],
            "start": slot["start"],
            "end": slot["end"],
            "room": room,
        }
        self.task_state["scheduled"] = dict(self.scheduled)
        self.current_step += 1

        done = len(self.scheduled) >= len(self.meetings)

        remaining = [m["id"] for m in self.meetings if m["id"] not in self.scheduled]

        return {
            "observation": {
                **self.get_visible_data(),
                "scheduled": dict(self.scheduled),
                "remaining_meetings": remaining,
            },
            "is_valid": True,
            "feedback": (
                f"Meeting '{meeting_id}' scheduled: {slot['day']} "
                f"{slot['start']}-{slot['end']} in {room}. "
                f"({len(self.scheduled)}/{len(self.meetings)} done)"
            ),
            "done": done,
        }

    def _handle_resolve_conflict(self, payload: dict) -> dict:
        """Handle conflict resolution (if agent needs to reschedule)."""
        self.current_step += 1
        conflict_id = payload.get("conflict_id", "")
        resolution = payload.get("resolution", "")

        if resolution == "reschedule" and conflict_id in self.scheduled:
            del self.scheduled[conflict_id]
            self.task_state["scheduled"] = dict(self.scheduled)
            return {
                "observation": self.get_visible_data(),
                "is_valid": True,
                "feedback": f"Meeting '{conflict_id}' unscheduled. Please propose a new slot.",
                "done": False,
            }

        return {
            "observation": self.get_visible_data(),
            "is_valid": False,
            "feedback": f"Invalid resolution for conflict '{conflict_id}'.",
            "done": False,
        }

    def get_visible_data(self) -> dict:
        data = self.get_initial_observation()
        data["current_schedule"] = dict(self.scheduled)
        data["remaining_meetings"] = [
            m["id"] for m in self.meetings if m["id"] not in self.scheduled
        ]
        return data
