---
title: Workplace AI Environment++
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---
# WorkplaceAIEnv++ — Multi-Agent Decision Intelligence Environment

A production-grade, OpenEnv-compliant reinforcement learning environment simulating real-world workplace decision-making. Built for the **Meta OpenEnv Hackathon**.

## 🎯 Overview

WorkplaceAIEnv++ challenges AI agents to handle complex workplace scenarios involving:

1. **Email Triage** (Easy) — Classify emails and assign priority scores
2. **Meeting Scheduling** (Medium) — Constraint-based scheduling with conflict resolution
3. **Workflow Execution** (Hard) — Multi-step task extraction, assignment, and response composition

### Key Features

- ✅ **OpenEnv compliant** — Passes `openenv validate`
- 🧠 **Partial observability** — Agent never sees ground truth
- 🔗 **State memory** — Multi-step tasks require context tracking
- 📐 **Structured action space** — Typed JSON actions, not free-form text
- 🎯 **Deterministic graders** — Same input → same score, always
- 💰 **Dense reward shaping** — Granular per-step feedback with completion bonuses
- 🐳 **Containerized** — Docker + Hugging Face Spaces ready

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (required — 3.14 has setuptools compatibility issues)
- **Docker Desktop** (for containerization)
- **Git** (for version control)

### 1. Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd meta

# Create virtual environment with Python 3.11
C:\Python311\python.exe -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Upgrade pip + setuptools
pip install --upgrade pip setuptools wheel

# Install project in editable mode with dev dependencies
pip install -e ".[dev]"

# Setup environment variables
copy .env.example .env
# Edit .env with your HF_TOKEN (see step 2 below)
```

### 2. Get Your Free Hugging Face Token

1. Go to [https://huggingface.co/join](https://huggingface.co/join) (sign up — it's free)
2. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Click **"New token"** → Name: `workplace-ai-env` → Role: **Read**
4. Copy the token (starts with `hf_...`)
5. Add it to your `.env` file: `HF_TOKEN=hf_your_token_here`

### 3. Run the Environment Server

```bash
python -m uvicorn workplace_ai_env.server.app:app --host 0.0.0.0 --port 8000
```

### 4. Run Inference

```bash
# Run all tasks
python inference.py

# Run a specific task
python inference.py --task email_triage --seed 0
```

### 5. Run Tests

```bash
python -m pytest workplace_ai_env/tests/ -v
```

## 📐 Architecture

```
workplace_ai_env/
├── openenv.yaml              # OpenEnv manifest
├── models.py                 # Action, Observation, State (Pydantic)
├── server/
│   ├── app.py                # FastAPI server
│   └── workplace_environment.py  # Core environment
├── tasks/                    # Task engines
│   ├── email_triage.py
│   ├── meeting_scheduler.py
│   └── workflow_executor.py
├── graders/                  # Deterministic graders
├── rewards/                  # Reward shaping
├── scenarios/                # Deterministic test scenarios
└── tests/                    # Test suite
```

## 🧩 Tasks

### Task 1: Email Triage (Easy)
- **Input**: 5 emails with subject, sender, body snippet
- **Action**: `classify_email` with category (`urgent`/`normal`/`spam`) and priority (0-1)
- **Grading**: Category accuracy (60%) + Priority distance (40%)

### Task 2: Meeting Scheduler (Medium)
- **Input**: 3 meetings, participant availability, room list
- **Action**: `propose_slot` with day, time, room
- **Constraints**: No overlap, room capacity, blocked hours, 30-min buffers
- **Grading**: Validity (40%) + Day match (20%) + Time proximity (20%) + Room match (20%)

### Task 3: Workflow Executor (Hard)
- **Input**: Email thread, team members, task board
- **Actions**: `extract_tasks` → `assign_task` (×N) → `compose_response`
- **Requires**: State memory across steps
- **Grading**: Extraction recall/precision, assignment quality, response requirements

## 🐳 Docker Validated

You can run the environment as a standalone Docker container. The `.env` file is safely excluded via `.dockerignore`.

```bash
# 1. Build the Docker image
docker build -t workplace-ai-env:latest .

# 2. Run the container (detached mode)
docker run -d --name workplace-test -p 8000:8000 workplace-ai-env:latest

# 3. Test the endpoints
# Health
curl http://localhost:8000/health
# Reset
curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d "{\\"task_name\\":\\"email_triage\\"}"
# Step
curl -X POST http://localhost:8000/step -H "Content-Type: application/json" -d "{\\"task_name\\":\\"email_triage\\",\\"action_type\\":\\"classify_email\\",\\"payload\\":{\\"email_id\\":\\"email_001\\",\\"category\\":\\"urgent\\",\\"priority\\":0.92}}"
# State
curl http://localhost:8000/state

# 4. Stop and remove the container
docker stop workplace-test
docker rm workplace-test
```

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/reset` | Start new episode |
| `POST` | `/step` | Execute an action |
| `GET` | `/state` | Get current state |

## 📋 Inference Output Format

```
[START] task=email_triage env=workplace_ai_env model=meta-llama/Llama-3.1-8B-Instruct
[STEP] step=1 action=classify_email reward=0.85 done=false error=null
[END] success=true steps=5 rewards=0.85,0.90,0.75,1.00,0.80
```

## 📜 License

BSD-3-Clause
