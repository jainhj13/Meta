"""
Meeting Scheduler Scenarios — Constraint-based scheduling datasets.

Each scenario contains 3 meetings with participant constraints,
room availability, and ground truth optimal schedules.
"""

from __future__ import annotations

SCENARIOS: list[dict] = [
    {
        "id": "meeting_scenario_001",
        "meetings": [
            {
                "id": "mtg_001",
                "title": "Product Review",
                "duration_minutes": 60,
                "participants": ["alice", "bob", "charlie"],
                "priority": "high",
                "preferred_time": "morning",
            },
            {
                "id": "mtg_002",
                "title": "Sprint Planning",
                "duration_minutes": 90,
                "participants": ["alice", "diana", "eve"],
                "priority": "medium",
                "preferred_time": "afternoon",
            },
            {
                "id": "mtg_003",
                "title": "1:1 with Manager",
                "duration_minutes": 30,
                "participants": ["bob", "frank"],
                "priority": "low",
                "preferred_time": "any",
            },
        ],
        "participants": {
            "alice": {
                "blocked": [
                    {"day": "Mon", "start": "09:00", "end": "10:00"},
                    {"day": "Wed", "start": "14:00", "end": "16:00"},
                ],
            },
            "bob": {
                "blocked": [
                    {"day": "Tue", "start": "09:00", "end": "17:00"},
                ],
            },
            "charlie": {
                "blocked": [
                    {"day": "Mon", "start": "13:00", "end": "14:00"},
                ],
            },
            "diana": {
                "blocked": [
                    {"day": "Thu", "start": "09:00", "end": "12:00"},
                ],
            },
            "eve": {
                "blocked": [],
            },
            "frank": {
                "blocked": [
                    {"day": "Fri", "start": "09:00", "end": "12:00"},
                ],
            },
        },
        "rooms": [
            {"id": "room_a", "capacity": 4, "has_projector": True},
            {"id": "room_b", "capacity": 8, "has_projector": True},
            {"id": "room_c", "capacity": 2, "has_projector": False},
        ],
        "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "work_hours": {"start": "09:00", "end": "17:00"},
        "ground_truth": {
            "optimal_schedule": {
                "mtg_001": {
                    "day": "Mon",
                    "start": "10:00",
                    "end": "11:00",
                    "room": "room_a",
                },
                "mtg_002": {
                    "day": "Mon",
                    "start": "14:00",
                    "end": "15:30",
                    "room": "room_b",
                },
                "mtg_003": {
                    "day": "Mon",
                    "start": "11:30",
                    "end": "12:00",
                    "room": "room_c",
                },
            },
            "constraints": {
                "no_overlap": True,
                "room_capacity": True,
                "blocked_hours": True,
                "buffer_minutes": 30,
            },
        },
    },
    {
        "id": "meeting_scenario_002",
        "meetings": [
            {
                "id": "mtg_001",
                "title": "Client Demo",
                "duration_minutes": 90,
                "participants": ["alice", "bob", "charlie", "diana"],
                "priority": "high",
                "preferred_time": "morning",
            },
            {
                "id": "mtg_002",
                "title": "Team Retro",
                "duration_minutes": 60,
                "participants": ["bob", "charlie", "eve"],
                "priority": "medium",
                "preferred_time": "afternoon",
            },
            {
                "id": "mtg_003",
                "title": "Design Review",
                "duration_minutes": 45,
                "participants": ["alice", "eve", "frank"],
                "priority": "medium",
                "preferred_time": "morning",
            },
        ],
        "participants": {
            "alice": {
                "blocked": [
                    {"day": "Tue", "start": "09:00", "end": "11:00"},
                    {"day": "Thu", "start": "13:00", "end": "17:00"},
                ],
            },
            "bob": {
                "blocked": [
                    {"day": "Mon", "start": "09:00", "end": "12:00"},
                    {"day": "Fri", "start": "14:00", "end": "17:00"},
                ],
            },
            "charlie": {
                "blocked": [
                    {"day": "Wed", "start": "09:00", "end": "17:00"},
                ],
            },
            "diana": {
                "blocked": [
                    {"day": "Mon", "start": "14:00", "end": "16:00"},
                ],
            },
            "eve": {
                "blocked": [
                    {"day": "Tue", "start": "14:00", "end": "16:00"},
                ],
            },
            "frank": {
                "blocked": [
                    {"day": "Mon", "start": "09:00", "end": "11:00"},
                ],
            },
        },
        "rooms": [
            {"id": "room_a", "capacity": 4, "has_projector": True},
            {"id": "room_b", "capacity": 8, "has_projector": True},
            {"id": "room_c", "capacity": 2, "has_projector": False},
        ],
        "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "work_hours": {"start": "09:00", "end": "17:00"},
        "ground_truth": {
            "optimal_schedule": {
                "mtg_001": {
                    "day": "Tue",
                    "start": "11:00",
                    "end": "12:30",
                    "room": "room_b",
                },
                "mtg_002": {
                    "day": "Tue",
                    "start": "14:00",
                    "end": "15:00",
                    "room": "room_a",
                },
                "mtg_003": {
                    "day": "Mon",
                    "start": "11:00",
                    "end": "11:45",
                    "room": "room_a",
                },
            },
            "constraints": {
                "no_overlap": True,
                "room_capacity": True,
                "blocked_hours": True,
                "buffer_minutes": 30,
            },
        },
    },
    {
        "id": "meeting_scenario_003",
        "meetings": [
            {
                "id": "mtg_001",
                "title": "Budget Review",
                "duration_minutes": 120,
                "participants": ["alice", "bob", "diana", "frank"],
                "priority": "high",
                "preferred_time": "morning",
            },
            {
                "id": "mtg_002",
                "title": "Tech Deep Dive",
                "duration_minutes": 60,
                "participants": ["charlie", "eve"],
                "priority": "low",
                "preferred_time": "afternoon",
            },
            {
                "id": "mtg_003",
                "title": "Cross-team Sync",
                "duration_minutes": 45,
                "participants": ["alice", "charlie", "eve"],
                "priority": "medium",
                "preferred_time": "morning",
            },
        ],
        "participants": {
            "alice": {
                "blocked": [
                    {"day": "Mon", "start": "09:00", "end": "10:30"},
                    {"day": "Wed", "start": "13:00", "end": "15:00"},
                ],
            },
            "bob": {
                "blocked": [
                    {"day": "Tue", "start": "09:00", "end": "12:00"},
                    {"day": "Thu", "start": "15:00", "end": "17:00"},
                ],
            },
            "charlie": {
                "blocked": [
                    {"day": "Mon", "start": "14:00", "end": "17:00"},
                ],
            },
            "diana": {
                "blocked": [],
            },
            "eve": {
                "blocked": [
                    {"day": "Fri", "start": "09:00", "end": "12:00"},
                ],
            },
            "frank": {
                "blocked": [
                    {"day": "Mon", "start": "09:00", "end": "11:00"},
                    {"day": "Wed", "start": "09:00", "end": "11:00"},
                ],
            },
        },
        "rooms": [
            {"id": "room_a", "capacity": 4, "has_projector": True},
            {"id": "room_b", "capacity": 8, "has_projector": True},
            {"id": "room_c", "capacity": 2, "has_projector": False},
        ],
        "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "work_hours": {"start": "09:00", "end": "17:00"},
        "ground_truth": {
            "optimal_schedule": {
                "mtg_001": {
                    "day": "Mon",
                    "start": "10:30",
                    "end": "12:30",
                    "room": "room_b",
                },
                "mtg_002": {
                    "day": "Mon",
                    "start": "14:00",
                    "end": "15:00",
                    "room": "room_c",
                },
                "mtg_003": {
                    "day": "Tue",
                    "start": "10:00",
                    "end": "10:45",
                    "room": "room_a",
                },
            },
            "constraints": {
                "no_overlap": True,
                "room_capacity": True,
                "blocked_hours": True,
                "buffer_minutes": 30,
            },
        },
    },
]


def get_scenario(seed: int = 0) -> dict:
    """Get a deterministic scenario based on seed."""
    idx = seed % len(SCENARIOS)
    return SCENARIOS[idx]
