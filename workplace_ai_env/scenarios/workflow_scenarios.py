"""
Workflow Executor Scenarios — Multi-step workflow datasets.

Each scenario has an email thread, team members, and ground truth
for task extraction, prioritization, assignment, and response.
"""

from __future__ import annotations

SCENARIOS: list[dict] = [
    {
        "id": "workflow_scenario_001",
        "email_thread": [
            {
                "id": "thread_001_msg_1",
                "from": "client@bigcorp.com",
                "to": "team@company.com",
                "subject": "Project Alpha - Deliverables Update",
                "body": (
                    "Hi team,\n\n"
                    "We need the following by Friday:\n"
                    "1. Updated wireframes for the mobile app\n"
                    "2. API documentation for the payment integration\n"
                    "3. Performance test results for the staging environment\n\n"
                    "Also, could someone fix the login bug that was reported yesterday?\n\n"
                    "Best,\nJameson (BigCorp PM)"
                ),
                "timestamp": "2024-03-14T10:00:00Z",
            },
            {
                "id": "thread_001_msg_2",
                "from": "manager@company.com",
                "to": "team@company.com",
                "subject": "RE: Project Alpha - Deliverables Update",
                "body": (
                    "Team, please prioritize these items. The client demo is next week.\n"
                    "The login bug is critical — fix it first.\n\n"
                    "Thanks,\nManager"
                ),
                "timestamp": "2024-03-14T10:30:00Z",
            },
        ],
        "team_members": [
            {"name": "alice", "role": "developer", "current_tasks": 3, "skills": ["backend", "api", "testing"]},
            {"name": "bob", "role": "designer", "current_tasks": 1, "skills": ["ui", "wireframes", "mobile"]},
            {"name": "charlie", "role": "qa_engineer", "current_tasks": 2, "skills": ["testing", "performance", "automation"]},
            {"name": "diana", "role": "developer", "current_tasks": 1, "skills": ["frontend", "mobile", "bugfix"]},
        ],
        "task_board": {
            "in_progress": ["Feature X backend", "Design system update", "CI pipeline fix"],
            "blocked": ["Database migration"],
        },
        "ground_truth": {
            "tasks": [
                {"id": "task_001", "description": "Update wireframes for mobile app", "priority": 2, "best_assignee": "bob", "deadline": "Friday"},
                {"id": "task_002", "description": "Write API documentation for payment integration", "priority": 3, "best_assignee": "alice", "deadline": "Friday"},
                {"id": "task_003", "description": "Run performance tests on staging environment", "priority": 3, "best_assignee": "charlie", "deadline": "Friday"},
                {"id": "task_004", "description": "Fix login bug", "priority": 1, "best_assignee": "diana", "deadline": "ASAP"},
            ],
            "priority_order": ["task_004", "task_001", "task_002", "task_003"],
            "response_must_include": [
                "acknowledge deliverables",
                "mention timeline",
                "reference login bug fix",
                "provide assignee names",
            ],
        },
    },
    {
        "id": "workflow_scenario_002",
        "email_thread": [
            {
                "id": "thread_002_msg_1",
                "from": "vp_engineering@company.com",
                "to": "team@company.com",
                "subject": "Q4 Launch Preparation - Action Items",
                "body": (
                    "Team,\n\n"
                    "For the Q4 launch we need:\n"
                    "1. Complete the database migration to PostgreSQL\n"
                    "2. Set up monitoring dashboards in Grafana\n"
                    "3. Update the deployment pipeline for zero-downtime releases\n"
                    "4. Write user migration guide for the breaking API changes\n\n"
                    "Deadlines:\n"
                    "- Database migration: End of next week\n"
                    "- Everything else: Two weeks from today\n\n"
                    "This is our top priority. Please de-prioritize non-critical work.\n\n"
                    "Regards,\nVP Engineering"
                ),
                "timestamp": "2024-03-18T09:00:00Z",
            },
        ],
        "team_members": [
            {"name": "alice", "role": "senior_developer", "current_tasks": 2, "skills": ["backend", "database", "postgresql"]},
            {"name": "bob", "role": "devops_engineer", "current_tasks": 1, "skills": ["devops", "monitoring", "grafana", "ci_cd"]},
            {"name": "charlie", "role": "developer", "current_tasks": 3, "skills": ["backend", "api", "documentation"]},
            {"name": "diana", "role": "developer", "current_tasks": 0, "skills": ["frontend", "devops", "deployment"]},
        ],
        "task_board": {
            "in_progress": ["Feature Y", "Bug triage"],
            "blocked": [],
        },
        "ground_truth": {
            "tasks": [
                {"id": "task_001", "description": "Complete database migration to PostgreSQL", "priority": 1, "best_assignee": "alice", "deadline": "end of next week"},
                {"id": "task_002", "description": "Set up monitoring dashboards in Grafana", "priority": 2, "best_assignee": "bob", "deadline": "two weeks"},
                {"id": "task_003", "description": "Update deployment pipeline for zero-downtime releases", "priority": 2, "best_assignee": "diana", "deadline": "two weeks"},
                {"id": "task_004", "description": "Write user migration guide for breaking API changes", "priority": 3, "best_assignee": "charlie", "deadline": "two weeks"},
            ],
            "priority_order": ["task_001", "task_002", "task_003", "task_004"],
            "response_must_include": [
                "acknowledge Q4 launch",
                "mention database migration priority",
                "provide timeline",
                "reference team assignments",
            ],
        },
    },
    {
        "id": "workflow_scenario_003",
        "email_thread": [
            {
                "id": "thread_003_msg_1",
                "from": "security@company.com",
                "to": "team@company.com",
                "subject": "URGENT: Security Vulnerability Found",
                "body": (
                    "CRITICAL SECURITY ALERT\n\n"
                    "Our security scan has identified the following vulnerabilities:\n"
                    "1. SQL injection vulnerability in the search API endpoint\n"
                    "2. Outdated TLS certificates on the payment gateway\n"
                    "3. Missing rate limiting on the authentication endpoints\n\n"
                    "Additionally, we need to:\n"
                    "- Conduct a full security audit of all public endpoints\n"
                    "- Update the incident response documentation\n\n"
                    "The SQL injection and TLS issues must be fixed within 24 hours.\n"
                    "Please treat this as highest priority.\n\n"
                    "- Security Team"
                ),
                "timestamp": "2024-03-19T07:00:00Z",
            },
            {
                "id": "thread_003_msg_2",
                "from": "cto@company.com",
                "to": "team@company.com",
                "subject": "RE: URGENT: Security Vulnerability Found",
                "body": (
                    "All hands on deck. Drop everything else.\n"
                    "I want hourly status updates on the critical fixes.\n\n"
                    "- CTO"
                ),
                "timestamp": "2024-03-19T07:15:00Z",
            },
        ],
        "team_members": [
            {"name": "alice", "role": "security_engineer", "current_tasks": 1, "skills": ["security", "backend", "sql", "audit"]},
            {"name": "bob", "role": "developer", "current_tasks": 2, "skills": ["backend", "api", "rate_limiting"]},
            {"name": "charlie", "role": "devops_engineer", "current_tasks": 1, "skills": ["devops", "tls", "certificates", "infrastructure"]},
            {"name": "diana", "role": "technical_writer", "current_tasks": 0, "skills": ["documentation", "security_policies"]},
        ],
        "task_board": {
            "in_progress": ["Feature Z", "Code review backlog", "CI improvements"],
            "blocked": [],
        },
        "ground_truth": {
            "tasks": [
                {"id": "task_001", "description": "Fix SQL injection vulnerability in search API", "priority": 1, "best_assignee": "alice", "deadline": "24 hours"},
                {"id": "task_002", "description": "Update TLS certificates on payment gateway", "priority": 1, "best_assignee": "charlie", "deadline": "24 hours"},
                {"id": "task_003", "description": "Implement rate limiting on authentication endpoints", "priority": 2, "best_assignee": "bob", "deadline": "48 hours"},
                {"id": "task_004", "description": "Conduct full security audit of public endpoints", "priority": 3, "best_assignee": "alice", "deadline": "1 week"},
                {"id": "task_005", "description": "Update incident response documentation", "priority": 3, "best_assignee": "diana", "deadline": "1 week"},
            ],
            "priority_order": ["task_001", "task_002", "task_003", "task_004", "task_005"],
            "response_must_include": [
                "acknowledge security alert",
                "mention 24-hour deadline",
                "reference SQL injection fix",
                "mention TLS certificate update",
                "provide status update plan",
            ],
        },
    },
]


def get_scenario(seed: int = 0) -> dict:
    """Get a deterministic scenario based on seed."""
    idx = seed % len(SCENARIOS)
    return SCENARIOS[idx]
