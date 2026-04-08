"""
Scenario Generator — Deterministic scenario selection based on seed.
"""

from __future__ import annotations

from workplace_ai_env.scenarios import email_scenarios, meeting_scenarios, workflow_scenarios


def get_scenario(task_name: str, seed: int = 0) -> dict:
    """
    Get a deterministic scenario for the given task.

    Args:
        task_name: One of 'email_triage', 'meeting_scheduler', 'workflow_executor'
        seed: Integer seed for reproducible scenario selection

    Returns:
        Complete scenario dict with data and ground truth
    """
    generators = {
        "email_triage": email_scenarios.get_scenario,
        "meeting_scheduler": meeting_scenarios.get_scenario,
        "workflow_executor": workflow_scenarios.get_scenario,
    }

    if task_name not in generators:
        raise ValueError(f"Unknown task: {task_name}. Valid: {list(generators.keys())}")

    return generators[task_name](seed)
