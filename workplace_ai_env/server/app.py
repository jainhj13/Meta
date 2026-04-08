"""
FastAPI Application for WorkplaceAIEnv++.

Exposes the environment over HTTP endpoints compatible with OpenEnv:
- POST /reset — Start a new episode
- POST /step — Execute an action
- GET /state — Get current state
- GET /health — Health check
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from workplace_ai_env.models import WorkplaceAction, WorkplaceObservation, WorkplaceState
from workplace_ai_env.server.workplace_environment import WorkplaceEnvironment


# ---- Request / Response Models ----

class ResetRequest(BaseModel):
    task_name: str = "email_triage"
    seed: int = 0
    episode_id: str | None = None


class StepRequest(BaseModel):
    task_name: str
    action_type: str
    payload: dict[str, Any] = {}


class StepResponse(BaseModel):
    observation: dict[str, Any]
    reward: float
    done: bool
    info: dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str = "healthy"
    environment: str = "workplace_ai_env"
    version: str = "1.0.0"


# ---- Application ----

# Global environment instance
env = WorkplaceEnvironment()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="WorkplaceAIEnv++",
    description="Multi-Agent Decision Intelligence Environment for OpenEnv",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.get("/metadata")
def metadata():
    return {
        "name": "WorkplaceAIEnv++",
        "description": "Multi-agent workplace decision intelligence environment with email triage, scheduling, and workflow execution tasks."
    }

@app.get("/schema")
def schema():
    return {
        "action": {
            "type": "object",
            "properties": {
                "task_name": {"type": "string"},
                "action_type": {"type": "string"},
                "payload": {"type": "object"}
            }
        },
        "observation": {
            "type": "object",
            "properties": {
                "visible_data": {"type": "object"},
                "instructions": {"type": "string"}
            }
        },
        "state": {
            "type": "object",
            "properties": {
                "step_number": {"type": "integer"},
                "done": {"type": "boolean"}
            }
        }
    }

@app.post("/mcp")
def mcp():
    return {
        "jsonrpc": "2.0",
        "result": "ok",
        "id": 1
    }


@app.post("/reset")
async def reset(request: ResetRequest) -> dict:
    """
    Reset the environment and start a new episode.

    Args:
        request: ResetRequest with task_name, seed, and optional episode_id

    Returns:
        Initial observation
    """
    try:
        observation = env.reset(
            task_name=request.task_name,
            seed=request.seed,
            episode_id=request.episode_id,
        )
        return observation.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest) -> StepResponse:
    """
    Execute one step in the environment.

    Args:
        request: StepRequest with task_name, action_type, and payload

    Returns:
        StepResponse with observation, reward, done, and info
    """
    try:
        action = WorkplaceAction(
            task_name=request.task_name,
            action_type=request.action_type,
            payload=request.payload,
        )
        result = env.step(action)
        return StepResponse(
            observation=result.observation.model_dump(),
            reward=result.reward,
            done=result.done,
            info=result.info,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
async def get_state() -> dict:
    """Get the current environment state."""
    try:
        return env.state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State failed: {str(e)}")


# ---- Direct execution ----

def main():
    """Entry point for direct execution."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
