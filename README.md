---
title: Workplace AI Environment++
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---

# WorkplaceAIEnv++ — Multi-Agent Decision Intelligence Environment

> **Meta OpenEnv Hackathon Submission** · OpenEnv 1.0.0 · ✅ 6/6 Validation Passed

A production-grade, OpenEnv-compliant reinforcement learning environment that simulates real-world workplace decision-making. AI agents must handle email triage, constraint-based meeting scheduling, and multi-step workflow execution — all graded deterministically with dense reward shaping.

**🌐 Live Deployment:** [https://theeagle84-workplace-ai-env.hf.space](https://theeagle84-workplace-ai-env.hf.space)

---

## 🧭 Problem & Motivation

Enterprise AI systems fail when agents can't make structured, multi-step decisions under realistic constraints. Most existing RL environments are toy simulations — abstract, stateless, and disconnected from real organizational workflows.

## 🏆 Highlights for Evaluation

- ✅ Fully OpenEnv compliant (6/6 validation passed)
- ✅ Real-world task simulation (no toy problems)
- ✅ Deterministic grading (zero LLM dependency in scoring)
- ✅ Dense reward shaping (step-level feedback)
- ✅ Multi-step reasoning tasks (memory + planning required)
- ✅ Fully deployable (Docker + Hugging Face Spaces)

## 🌍 Why This Matters

Most evaluation benchmarks fail to capture real-world complexity.

WorkplaceAIEnv++ introduces:
- structured decision-making instead of free-form generation
- multi-step workflows instead of single-step tasks
- deterministic grading for reproducibility

This makes it suitable for benchmarking **enterprise-grade AI agents**.

**WorkplaceAIEnv++** closes this gap by providing a fully observable, stateful, and deterministically graded environment where agents must:

- Classify and prioritize communications under ambiguity
- Schedule meetings across overlapping participant constraints
- Coordinate multi-phase task extraction, assignment, and composition

Each task requires structured JSON actions, not free-form text — enforcing the kind of precision real enterprise systems demand.

---

## ✅ OpenEnv Validation

| Check | Status |
|-------|--------|
| Endpoint schema compliance (`/reset`, `/step`, `/state`) | ✅ Passed |
| Action/observation contract | ✅ Passed |
| Reward signal correctness | ✅ Passed |
| Episode termination logic | ✅ Passed |
| Deterministic grader consistency | ✅ Passed |
| OpenEnv manifest (`openenv.yaml`) | ✅ Passed |
| **Total** | **6 / 6** |

Validated against `openenv-http/1.x` standard profile, spec version `1.0.0`.

---

## 🔑 Key Features

| Feature | Detail |
|---------|--------|
| **OpenEnv Compliant** | Passes `openenv validate` — all 6 checks green |
| **3 Distinct Tasks** | Easy → Medium → Hard progression |
| **Deterministic Graders** | Same input always produces the same score |
| **Dense Reward Shaping** | Granular per-step feedback + episode completion bonuses |
| **Partial Observability** | Agent never sees ground truth labels |
| **Stateful Episodes** | Multi-step tasks require cross-step context tracking |
| **Typed Action Space** | Structured JSON actions — no free-form text |
| **Containerized** | Docker + Hugging Face Spaces deployment |
| **HF Inference Ready** | Works with any model via `huggingface_hub.InferenceClient` |

---

## 📋 Tasks Overview

| # | Task | Difficulty | Steps | Action Types | Grading Criteria |
|---|------|-----------|-------|--------------|-----------------|
| 1 | `email_triage` | 🟢 Easy | 5 | `classify_email` | Category accuracy (60%) + Priority distance (40%) |
| 2 | `meeting_scheduler` | 🟡 Medium | 3 | `propose_slot` | Validity (40%) + Day (20%) + Time proximity (20%) + Room (20%) |
| 3 | `workflow_executor` | 🔴 Hard | N+2 | `extract_tasks` → `assign_task` × N → `compose_response` | Extraction recall/precision, assignment quality, response completeness |

---

## 🗂️ Architecture

```
workplace_ai_env/
├── openenv.yaml                      # OpenEnv manifest (spec_version: 1)
├── models.py                         # Pydantic models: Action, Observation, State
├── server/
│   ├── app.py                        # FastAPI application
│   └── workplace_environment.py      # Core episode + state management
├── tasks/
│   ├── email_triage.py               # Task engine: email classification
│   ├── meeting_scheduler.py          # Task engine: constraint-based scheduling
│   └── workflow_executor.py          # Task engine: multi-phase workflow
├── graders/                          # Deterministic graders (per task)
├── rewards/                          # Dense reward shaping logic
├── scenarios/                        # Reproducible deterministic test scenarios
└── tests/                            # Full test suite
```

**Data flow:**

```
inference.py  →  /reset  →  Observation
     ↓                          ↓
   LLM  →  JSON action  →  /step  →  (reward, done, next observation)
                                           ↑
                               Deterministic grader + reward shaper
```

---

## 🌐 API Endpoints

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `GET` | `/health` | — | Health check — returns `{"status": "ok"}` |
| `POST` | `/reset` | `{"task_name": "...", "seed": 0}` | Start a new episode, returns initial observation |
| `POST` | `/step` | `{"task_name": "...", "action_type": "...", "payload": {...}}` | Execute one action, returns reward + next observation |
| `GET` | `/state` | — | Inspect full current environment state |

### Example: Email Triage Step

```bash
# Reset
curl -X POST https://theeagle84-workplace-ai-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "email_triage", "seed": 0}'

# Step
curl -X POST https://theeagle84-workplace-ai-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"task_name": "email_triage", "action_type": "classify_email", "payload": {"email_id": "email_001", "category": "urgent", "priority": 0.92}}'
```

---

## 🧩 Task Details

### Task 1: Email Triage (Easy)

- **Input:** 5 emails — subject, sender, body snippet
- **Action:** `classify_email` with `category` (`urgent` / `normal` / `spam`) and `priority` (0.0–1.0)
- **Reward:** Category accuracy 60% + inverse priority distance 40%

### Task 2: Meeting Scheduler (Medium)

- **Input:** 3 meetings, participant availability, room list
- **Action:** `propose_slot` with `day`, `start`, `end`, `room`
- **Constraints:** No room overlap, participant conflicts, 30-min buffers, room capacity, work-hours bounds
- **Reward:** Slot validity 40% + day match 20% + time proximity 20% + room match 20%

### Task 3: Workflow Executor (Hard)

- **Input:** Email thread, team roster, task board
- **Actions (in order):**
  1. `extract_tasks` — extract all action items from the thread
  2. `assign_task` × N — assign each task to a valid team member
  3. `compose_response` — write a professional summary email
- **Requires:** State memory across steps (phase tracking)
- **Reward:** Extraction recall/precision + assignment coverage + response completeness

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (required — 3.14 has setuptools compatibility issues)
- **Docker Desktop** (for local containerization)
- **Git**

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd meta

# Create virtual environment
C:\Python311\python.exe -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"

# Configure environment
copy .env.example .env
# Edit .env: add your HF_TOKEN
```

### 2. Get a Hugging Face Token (Free)

1. Sign up at [huggingface.co/join](https://huggingface.co/join)
2. Go to [Settings → Tokens](https://huggingface.co/settings/tokens)
3. Create a token with **Read** permission
4. Add to `.env`: `HF_TOKEN=hf_your_token_here`

### 3. Start the Environment Server

```bash
python -m uvicorn workplace_ai_env.server.app:app --host 0.0.0.0 --port 8000
```

### 4. Run Inference

```bash
# Run all 3 tasks
python inference.py

# Run a specific task with seed
python inference.py --task email_triage --seed 0
python inference.py --task meeting_scheduler --seed 0
python inference.py --task workflow_executor --seed 0
```

### 5. Run Tests

```bash
python -m pytest workplace_ai_env/tests/ -v
```

---

## 📐 Inference Output Format

The inference script follows a **strict, machine-parseable output format** required by OpenEnv evaluators. No deviation is permitted.

```
[START] task=<task_name> env=workplace_ai_env model=<model_name>
[STEP] step=<n> action=<action_type> reward=<0.00> done=<true|false> error=<msg|null>
[END] success=<true|false> steps=<n> rewards=<comma-separated-floats>
```

**Example — email_triage run:**

```
[START] task=email_triage env=workplace_ai_env model=meta-llama/Llama-3.1-8B-Instruct
[STEP] step=1 action=classify_email reward=0.85 done=false error=null
[STEP] step=2 action=classify_email reward=0.90 done=false error=null
[STEP] step=3 action=classify_email reward=0.75 done=false error=null
[STEP] step=4 action=classify_email reward=1.00 done=false error=null
[STEP] step=5 action=classify_email reward=0.80 done=true error=null
[END] success=true steps=5 rewards=0.85,0.90,0.75,1.00,0.80
```

**Rules:**
- `reward` is always formatted to 2 decimal places
- `done` is lowercase `true` or `false`
- `error` is `null` on success, or a short message on failure
- `[END]` always prints, even on failure

---

## 🐳 Docker

```bash
# Build
docker build -t workplace-ai-env:latest .

# Run (detached)
docker run -d --name workplace-test -p 8000:8000 workplace-ai-env:latest

# Verify
curl http://localhost:8000/health

# Stop & clean up
docker stop workplace-test && docker rm workplace-test
```

The `.env` file is excluded via `.dockerignore` — credentials are never baked into the image.

---

## 📁 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | *(required)* | Hugging Face API token |
| `MODEL_NAME` | `meta-llama/Llama-3.1-8B-Instruct` | Model for inference |
| `API_BASE_URL` | `https://router.huggingface.co/hf-inference/v1` | HF Inference API base |
| `ENV_SERVER_URL` | `http://localhost:8000` | Environment server URL |

---

## 🔗 Submission Links

- 🌐 Hugging Face Space: https://theeagle84-workplace-ai-env.hf.space
- 💻 GitHub Repository: https://github.com/explorer2005/Meta

## 📜 License

BSD-3-Clause
