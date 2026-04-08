"""
WorkplaceAIEnv++ Inference Script

CRITICAL: This script follows the STRICT output format required by OpenEnv.

Usage:
    python inference.py                                    # Run all tasks
    python inference.py --task email_triage                # Run specific task
    python inference.py --task meeting_scheduler --seed 1  # With seed

Environment Variables (set in .env):
    HF_TOKEN        - Hugging Face API token (REQUIRED)
    API_BASE_URL    - HF Inference API URL (default: https://api-inference.huggingface.co/v1)
    MODEL_NAME      - Model name (default: meta-llama/Llama-3.1-8B-Instruct)
    ENV_SERVER_URL  - Environment server URL (default: http://localhost:8000)

Output Format (STRICT — NO DEVIATION):
    [START] task=<task_name> env=workplace_ai_env model=<model_name>
    [STEP] step=<n> action=<action> reward=<0.00> done=<true|false> error=<msg|null>
    [END] success=<true|false> steps=<n> rewards=<comma-separated>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import httpx
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/hf-inference/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
ENV_SERVER_URL = os.getenv("ENV_SERVER_URL", "http://localhost:8000")

# Validate token
if not HF_TOKEN or HF_TOKEN == "hf_your_token_here":
    print("ERROR: HF_TOKEN not set. Please configure your .env file.", file=sys.stderr)
    print("Steps:", file=sys.stderr)
    print("  1. Go to https://huggingface.co/settings/tokens", file=sys.stderr)
    print("  2. Create a token with 'Read' permission", file=sys.stderr)
    print("  3. Add it to your .env file: HF_TOKEN=hf_...", file=sys.stderr)
    sys.exit(1)


def create_llm_client() -> InferenceClient:
    """Create InferenceClient for Hugging Face."""
    return InferenceClient(api_key=HF_TOKEN)


def env_reset(task_name: str, seed: int = 0) -> dict:
    """Call the environment's reset endpoint."""
    response = httpx.post(
        f"{ENV_SERVER_URL}/reset",
        json={"task_name": task_name, "seed": seed},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def env_step(action: dict) -> dict:
    """Call the environment's step endpoint."""
    response = httpx.post(
        f"{ENV_SERVER_URL}/step",
        json=action,
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def build_system_prompt(task_name: str) -> str:
    """Build task-specific system prompt for the LLM."""
    base = (
        "You are an AI workplace assistant. You must respond with ONLY valid JSON. "
        "No explanations, no markdown, no extra text. Just the raw JSON object.\n\n"
    )

    if task_name == "email_triage":
        return base + (
            "Task: Classify an email as 'urgent', 'normal', or 'spam' and assign a priority score (0.0-1.0).\n"
            "Response format: {\"email_id\": \"<id>\", \"category\": \"<urgent|normal|spam>\", \"priority\": <0.0-1.0>}\n"
        )
    elif task_name == "meeting_scheduler":
        return base + (
            "Task: Schedule meetings by proposing valid time slots one at a time.\n"
            "Response format: {\"meeting_id\": \"<id>\", \"slot\": {\"day\": \"<Mon|Tue|Wed|Thu|Fri>\", \"start\": \"HH:MM\", \"end\": \"HH:MM\"}, \"room\": \"<room_id>\"}\n"
            "CRITICAL RULES you MUST follow or the slot will be REJECTED:\n"
            "1. The slot duration (end minus start) must EXACTLY match the meeting's duration_minutes.\n"
            "2. start and end must be within work hours (check work_hours in the state).\n"
            "3. Do NOT use a blocked time slot for any participant in the meeting.\n"
            "4. Choose a room whose capacity >= number of participants.\n"
            "5. Leave at least 30 minutes gap between meetings sharing a participant on the same day.\n"
            "6. Do NOT overlap in the same room on the same day.\n"
            "7. Only schedule one meeting per response. Pick the first unscheduled meeting from remaining_meetings.\n"
            "8. Use a completely different day or time if previous attempt for the same meeting was rejected.\n"
        )
    elif task_name == "workflow_executor":
        return base + (
            "Task: Execute a 3-phase workflow in strict order.\n"
            "Phase 1 — extract_tasks (do this FIRST): Read the email thread carefully and extract ALL action items.\n"
            "  Response: {\"tasks\": [{\"id\": \"task_001\", \"description\": \"<action item>\", \"priority\": <1-5>}, ...]}\n"
            "  Rules: 'tasks' must be a NON-EMPTY list. Use sequential IDs: task_001, task_002, etc.\n"
            "Phase 2 — assign_task (repeat for EACH task): Assign one task per response.\n"
            "  Response: {\"task_id\": \"<exact id from extracted tasks>\", \"assignee\": \"<exact team member name from team_members list>\", \"deadline\": \"<date or timeframe>\"}\n"
            "  CRITICAL: 'assignee' must be an EXACT name from the team_members list in the current state.\n"
            "Phase 3 — compose_response (do this LAST, once all tasks assigned): Write a professional reply.\n"
            "  Response: {\"response_text\": \"<at least 20 characters>\", \"action_items\": [\"<item1>\", ...]}\n"
            "Always check current_phase in the state to know which phase to execute.\n"
        )
    return base


def build_user_prompt(observation: dict, task_name: str, step: int) -> str:
    """Build the user prompt from the current observation."""
    visible = observation.get("visible_data", {})
    feedback = observation.get("feedback", "")
    available = observation.get("available_actions", [])

    prompt = f"Step {step}. You MUST use action type: {available[0] if available else 'none'}\n"
    if feedback:
        prompt += f"Previous result: {feedback}\n"

    # For meeting_scheduler, highlight remaining meetings and constraints prominently
    if task_name == "meeting_scheduler":
        remaining = visible.get("remaining_meetings", [])
        scheduled = visible.get("current_schedule", {})
        work_hours = visible.get("work_hours", {})
        rooms = visible.get("rooms", [])
        meetings = visible.get("meetings", [])
        availability = visible.get("participant_availability", {})

        if remaining:
            next_meeting_id = remaining[0]
            next_meeting = next((m for m in meetings if m["id"] == next_meeting_id), {})
            duration = next_meeting.get("duration_minutes", 60)
            participants = next_meeting.get("participants", [])
            preferred = next_meeting.get("preferred_time", "")

            suitable_rooms = [r for r in rooms if r["capacity"] >= len(participants)]

            prompt += f"\nSCHEDULE THIS MEETING NEXT: {next_meeting_id}\n"
            prompt += f"  Duration: EXACTLY {duration} minutes (end = start + {duration} min)\n"
            prompt += f"  Participants: {participants}\n"
            prompt += f"  Preferred time: {preferred}\n"
            prompt += f"  Work hours: {work_hours.get('start','09:00')} - {work_hours.get('end','18:00')}\n"
            prompt += f"  Suitable rooms (capacity >= {len(participants)}): {[r['id'] for r in suitable_rooms]}\n"
            prompt += f"  Blocked times per participant:\n"
            for p in participants:
                blocks = availability.get(p, {}).get("blocked_slots", [])
                if blocks:
                    prompt += f"    {p}: {blocks}\n"
                else:
                    prompt += f"    {p}: no blocks\n"
            if scheduled:
                prompt += f"  Already scheduled (avoid overlap + 30min buffer for shared participants):\n"
                for sid, sinfo in scheduled.items():
                    prompt += f"    {sid}: {sinfo}\n"
        prompt += "\nRespond with ONLY the JSON for propose_slot."

    elif task_name == "workflow_executor":
        phase = visible.get("current_phase", "extract_tasks")
        team = visible.get("team_members", [])
        extracted = visible.get("extracted_tasks", [])
        assignments = visible.get("assignments", {})

        prompt += f"\nCurrent phase: {phase}\n"
        if phase == "assign_task" and extracted:
            unassigned = [t["id"] for t in extracted if t["id"] not in assignments]
            team_names = [tm["name"] for tm in team]
            prompt += f"  Extracted tasks: {extracted}\n"
            prompt += f"  Unassigned task IDs: {unassigned}\n"
            prompt += f"  Valid assignee names (use EXACT spelling): {team_names}\n"
            if unassigned:
                prompt += f"  Assign THIS task next: {unassigned[0]}\n"
        elif phase == "compose_response":
            prompt += f"  All assignments done: {assignments}\n"
            prompt += "  Now compose a professional response email (response_text >= 20 chars).\n"
        else:
            prompt += f"\nCurrent state:\n{json.dumps(visible, indent=2, default=str)}\n"
        prompt += "\nRespond with ONLY the JSON for your next action."

    else:
        prompt += f"\nCurrent state:\n{json.dumps(visible, indent=2, default=str)}\n"
        prompt += "\nRespond with ONLY the JSON for your next action."

    return prompt


def parse_llm_response(response_text: str) -> dict:
    """Extract JSON from LLM response, handling common formatting issues."""
    text = response_text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    # Try finding JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return {}


def run_task(
    client: InferenceClient,
    task_name: str,
    seed: int = 0,
    max_retries: int = 2,
) -> bool:
    """
    Run a complete task episode.

    Returns:
        True if task completed successfully
    """
    # STRICT OUTPUT: Start marker
    print(f"[START] task={task_name} env=workplace_ai_env model={MODEL_NAME}")

    try:
        # Reset environment
        observation = env_reset(task_name, seed)
    except Exception as e:
        print(f"[STEP] step=0 action=reset reward=0.00 done=true error={e}")
        print(f"[END] success=false steps=0 rewards=")
        return False

    rewards: list[float] = []
    step_num = 0
    done = False
    system_prompt = build_system_prompt(task_name)
    messages = [{"role": "system", "content": system_prompt}]

    while not done and step_num < observation.get("max_steps", 10):
        step_num += 1
        available_actions = observation.get("available_actions", [])

        if not available_actions:
            print(f"[STEP] step={step_num} action=none reward=0.00 done=true error=no_actions_available")
            break

        action_type = available_actions[0]

        # Build prompt
        user_prompt = build_user_prompt(observation, task_name, step_num)
        messages.append({"role": "user", "content": user_prompt})

        # Call LLM
        error_msg = None
        payload = {}

        for retry in range(max_retries + 1):
            try:
                completion = client.chat_completion(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.1,
                )
                llm_response = completion.choices[0].message.content or ""
                payload = parse_llm_response(llm_response)

                if payload:
                    messages.append({"role": "assistant", "content": llm_response})
                    break
                else:
                    error_msg = "failed_to_parse_json"
            except Exception as e:
                error_msg = str(e)[:100]

        if not payload:
            print(f"[STEP] step={step_num} action={action_type} reward=0.00 done=false error={error_msg}")
            rewards.append(0.0)
            continue

        # Execute step
        try:
            step_result = env_step({
                "task_name": task_name,
                "action_type": action_type,
                "payload": payload,
            })

            reward = step_result.get("reward", 0.0)
            done = step_result.get("done", False)
            rewards.append(reward)
            observation = step_result.get("observation", observation)

            print(
                f"[STEP] step={step_num} action={action_type} "
                f"reward={reward:.2f} done={'true' if done else 'false'} error=null"
            )

        except Exception as e:
            error_msg = str(e)[:100]
            print(f"[STEP] step={step_num} action={action_type} reward=0.00 done=false error={error_msg}")
            rewards.append(0.0)

    # STRICT OUTPUT: End marker
    success = done and len(rewards) > 0
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={'true' if success else 'false'} steps={step_num} rewards={rewards_str}")

    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="WorkplaceAIEnv++ Inference")
    parser.add_argument(
        "--task",
        type=str,
        default="all",
        choices=["all", "email_triage", "meeting_scheduler", "workflow_executor"],
        help="Task to run (default: all)",
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    args = parser.parse_args()

    client = create_llm_client()

    tasks = (
        ["email_triage", "meeting_scheduler", "workflow_executor"]
        if args.task == "all"
        else [args.task]
    )

    results = {}
    for task in tasks:
        success = run_task(client, task, seed=args.seed)
        results[task] = success

    # Summary
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"Results: {passed}/{total} tasks completed successfully", file=sys.stderr)
    for task, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {task}", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)

    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
