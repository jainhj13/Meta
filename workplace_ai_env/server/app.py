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
from typing import Any, Optional

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

from workplace_ai_env.models import WorkplaceAction, WorkplaceObservation, WorkplaceState
from workplace_ai_env.server.workplace_environment import WorkplaceEnvironment


# ---- Request / Response Models ----

class ResetRequest(BaseModel):
    """Request model for environment reset endpoint."""
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    
    task_name: str = Field(default="email_triage", description="Task name")
    seed: int = Field(default=0, description="Random seed")
    episode_id: Optional[str] = Field(default=None, description="Optional episode ID")


class StepRequest(BaseModel):
    """Request model for environment step endpoint."""
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    
    task_name: str = Field(default="", description="Task name")
    action_type: str = Field(default="", description="Action type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Action payload")


class StepResponse(BaseModel):
    """Response model for environment step endpoint."""
    model_config = ConfigDict(populate_by_name=True)
    
    observation: dict[str, Any] = Field(..., description="Next observation")
    reward: float = Field(..., description="Reward for this step")
    done: bool = Field(..., description="Whether episode is done")
    info: dict[str, Any] = Field(default_factory=dict, description="Additional info")


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
async def reset(request: Request):
    """Reset - no validation, pure request handling"""
    try:
        body = {}
        try:
            body = await request.json()
        except:
            pass
        
        if not isinstance(body, dict):
            body = {}
        
        task_name = body.get("task_name") or "email_triage"
        seed = int(body.get("seed", 0))
        episode_id = body.get("episode_id")
        
        observation = env.reset(
            task_name=str(task_name),
            seed=seed,
            episode_id=str(episode_id) if episode_id else None,
        )
        result = observation.model_dump()
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        import traceback
        return JSONResponse(content={"error": str(e), "traceback": traceback.format_exc()}, status_code=500)


@app.post("/step")
async def step(request_obj: Request):
    """Step - no validation, pure request handling"""
    try:
        body = {}
        try:
            body = await request_obj.json()
        except:
            pass
        
        if not isinstance(body, dict):
            body = {}
        
        action = WorkplaceAction(
            task_name=str(body.get("task_name", "")),
            action_type=str(body.get("action_type", "")),
            payload=dict(body.get("payload", {})),
        )
        result = env.step(action)
        response = {
            "observation": result.observation.model_dump(),
            "reward": result.reward,
            "done": result.done,
            "info": result.info,
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        import traceback
        return JSONResponse(content={"error": str(e), "traceback": traceback.format_exc()}, status_code=500)


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
