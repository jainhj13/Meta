"""
Email Triage Scenarios — Deterministic email datasets.

Each scenario contains 5 emails with hidden ground truth labels.
Scenarios are selected by seed for reproducibility.
"""

from __future__ import annotations

SCENARIOS: list[dict] = [
    {
        "id": "email_scenario_001",
        "emails": [
            {
                "id": "email_001",
                "from": "ceo@company.com",
                "subject": "URGENT: Board meeting moved to tomorrow",
                "body_snippet": "Team, the board meeting has been moved to tomorrow morning. We need all Q3 reports finalized by tonight. Please prioritize this above everything else.",
                "timestamp": "2024-03-15T08:30:00Z",
                "has_attachment": True,
            },
            {
                "id": "email_002",
                "from": "newsletter@marketing-platform.io",
                "subject": "🎉 You won't BELIEVE these deals! Act NOW!!!",
                "body_snippet": "Dear valued customer, click here for EXCLUSIVE offers that expire in 2 hours! Unsubscribe link at bottom. This is a promotional message.",
                "timestamp": "2024-03-15T07:00:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_003",
                "from": "sarah.chen@company.com",
                "subject": "Weekly standup notes - March 15",
                "body_snippet": "Hi team, here are the notes from today's standup. Alice is working on the API redesign, Bob is finishing the test suite, and I'm updating the docs.",
                "timestamp": "2024-03-15T10:15:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_004",
                "from": "security@company.com",
                "subject": "CRITICAL: Production server alert - immediate action required",
                "body_snippet": "ALERT: Production database CPU at 98%. Multiple services degraded. On-call team has been paged. Need engineering lead to authorize emergency scaling.",
                "timestamp": "2024-03-15T11:45:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_005",
                "from": "hr@company.com",
                "subject": "Updated PTO policy - effective next quarter",
                "body_snippet": "Dear employees, please review the attached updated PTO policy document. Changes include increased carryover days and a new sabbatical program starting Q2.",
                "timestamp": "2024-03-15T09:30:00Z",
                "has_attachment": True,
            },
        ],
        "ground_truth": {
            "email_001": {"category": "urgent", "priority": 0.92},
            "email_002": {"category": "spam", "priority": 0.05},
            "email_003": {"category": "normal", "priority": 0.35},
            "email_004": {"category": "urgent", "priority": 0.98},
            "email_005": {"category": "normal", "priority": 0.45},
        },
    },
    {
        "id": "email_scenario_002",
        "emails": [
            {
                "id": "email_001",
                "from": "client.vip@bigcorp.com",
                "subject": "Contract renewal deadline TODAY",
                "body_snippet": "Hi, our $2M contract renewal is due by end of business today. We need the signed documents ASAP or we risk losing this account. Legal has the final draft.",
                "timestamp": "2024-03-16T08:00:00Z",
                "has_attachment": True,
            },
            {
                "id": "email_002",
                "from": "team-building@company.com",
                "subject": "Friday pizza vote - pick your toppings!",
                "body_snippet": "Hey everyone! This Friday we're ordering pizza for the team lunch. Please reply with your preferred toppings. Vegetarian options will be available too.",
                "timestamp": "2024-03-16T09:00:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_003",
                "from": "no-reply@prize-winner-notification.xyz",
                "subject": "Congratulations! You've been selected for $10,000!",
                "body_snippet": "You have been randomly selected as our monthly winner! Click the link below to claim your prize. Provide your bank details to receive the transfer.",
                "timestamp": "2024-03-16T06:00:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_004",
                "from": "devops@company.com",
                "subject": "Scheduled maintenance window - this Saturday",
                "body_snippet": "Reminder: We have a planned maintenance window this Saturday from 2 AM to 6 AM EST. All staging environments will be unavailable during this time.",
                "timestamp": "2024-03-16T10:00:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_005",
                "from": "manager@company.com",
                "subject": "RE: Performance review - action items need immediate attention",
                "body_snippet": "Following up on yesterday's review. The items I flagged need to be addressed before the end of this sprint. Let's sync today to discuss the timeline.",
                "timestamp": "2024-03-16T08:30:00Z",
                "has_attachment": False,
            },
        ],
        "ground_truth": {
            "email_001": {"category": "urgent", "priority": 0.95},
            "email_002": {"category": "normal", "priority": 0.15},
            "email_003": {"category": "spam", "priority": 0.02},
            "email_004": {"category": "normal", "priority": 0.40},
            "email_005": {"category": "urgent", "priority": 0.80},
        },
    },
    {
        "id": "email_scenario_003",
        "emails": [
            {
                "id": "email_001",
                "from": "compliance@company.com",
                "subject": "URGENT: Regulatory audit response due in 4 hours",
                "body_snippet": "The regulatory body has requested additional documentation for our annual compliance audit. We must submit the response by 3 PM today or face penalties.",
                "timestamp": "2024-03-17T11:00:00Z",
                "has_attachment": True,
            },
            {
                "id": "email_002",
                "from": "intern@company.com",
                "subject": "Question about the onboarding process",
                "body_snippet": "Hi, I'm a new intern starting next week. Could someone point me to the onboarding guide? I want to set up my development environment beforehand.",
                "timestamp": "2024-03-17T14:00:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_003",
                "from": "deals@cheap-software-license.biz",
                "subject": "Get Microsoft Office for $9.99! Limited time only!",
                "body_snippet": "Genuine software licenses at unbelievable prices! Buy now and save 95%! All licenses are 100% genuine and come with lifetime warranty. Order today!",
                "timestamp": "2024-03-17T05:30:00Z",
                "has_attachment": False,
            },
            {
                "id": "email_004",
                "from": "cto@company.com",
                "subject": "Architecture decision needed - microservices migration",
                "body_snippet": "Team leads: we need to finalize the architecture decision for the microservices migration by this Friday. Please review the RFC and add your comments.",
                "timestamp": "2024-03-17T09:00:00Z",
                "has_attachment": True,
            },
            {
                "id": "email_005",
                "from": "facilities@company.com",
                "subject": "Office kitchen - new coffee machine installed",
                "body_snippet": "Good news! A new espresso machine has been installed in the 3rd floor kitchen. Quick guide is posted on the wall. Please keep the area clean.",
                "timestamp": "2024-03-17T13:00:00Z",
                "has_attachment": False,
            },
        ],
        "ground_truth": {
            "email_001": {"category": "urgent", "priority": 0.97},
            "email_002": {"category": "normal", "priority": 0.25},
            "email_003": {"category": "spam", "priority": 0.03},
            "email_004": {"category": "normal", "priority": 0.65},
            "email_005": {"category": "normal", "priority": 0.10},
        },
    },
]


def get_scenario(seed: int = 0) -> dict:
    """Get a deterministic scenario based on seed."""
    idx = seed % len(SCENARIOS)
    return SCENARIOS[idx]
