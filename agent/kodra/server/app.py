from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kodra.config import settings
from kodra.models.plan import ExecutionPlan, ExecutionResult, PlanStep, StepStatus, PlanStatus
from kodra.security.policy import SecurityPolicy, SecurityViolation
from kodra.engine.filesystem import FileSystemEngine
from kodra.engine.executor import CommandExecutor
from kodra.engine.runner import PlanRunner
from kodra.engine.healer import SelfHealingEngine
from kodra.memory.project_memory import ProjectMemoryManager
from kodra.providers.factory import ProviderFactory
from kodra.agents.orchestrator import LeadOrchestrator


app = FastAPI(title="Kodra Autonomous AI Coding Agent", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_services():
    ws = settings.workspace_root
    policy = SecurityPolicy(ws)
    fs = FileSystemEngine(ws, policy)
    executor = CommandExecutor(ws, default_timeout=settings.command_timeout_sec)
    runner = PlanRunner(ws, fs, executor, policy)
    healer = SelfHealingEngine(ws, fs)
    memory = ProjectMemoryManager(ws)
    orchestrator = LeadOrchestrator(ws)
    return {
        "workspace": ws,
        "policy": policy,
        "fs": fs,
        "executor": executor,
        "runner": runner,
        "healer": healer,
        "memory": memory,
        "orchestrator": orchestrator,
    }


# Request models
class WorkspaceSwitchRequest(BaseModel):
    path: str


class ConfigUpdateRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    ollama_host: Optional[str] = None


class PlanGenerationRequest(BaseModel):
    task: str
    multi_agent: bool = False
    context: Dict[str, Any] = {}


class PlanExecuteRequest(BaseModel):
    plan: ExecutionPlan
    approved_step_ids: Optional[List[str]] = None
    auto_approve: bool = False


class PlanRepairRequest(BaseModel):
    original_plan: ExecutionPlan
    failed_step_id: str
    error_output: str


class FileSaveRequest(BaseModel):
    path: str
    content: str


# --- Core Endpoints ---

@app.get("/")
def root():
    return {
        "name": "Kodra Agent",
        "status": "online",
        "version": "0.2.0",
        "active_workspace": str(settings.workspace_root),
        "active_provider": settings.provider,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/workspace")
def get_workspace():
    srv = get_services()
    files = srv["fs"].list_files(limit=500)
    config = srv["memory"].get_config()
    return {
        "workspace_root": str(settings.workspace_root),
        "project_name": config.name,
        "tech_stack": config.tech_stack,
        "files_count": len(files),
    }


@app.post("/workspace")
def set_workspace(req: WorkspaceSwitchRequest):
    try:
        resolved = settings.set_workspace(req.path)
        srv = get_services()
        config = srv["memory"].load_or_initialize()
        return {
            "status": "switched",
            "workspace_root": str(resolved),
            "project_name": config.name,
            "tech_stack": config.tech_stack,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/project")
def project():
    srv = get_services()
    files = srv["fs"].list_files(limit=500)
    config = srv["memory"].get_config()
    return {
        "project": config.name,
        "files": files,
        "tech_stack": config.tech_stack,
        "guidelines": config.guidelines,
    }


@app.get("/file")
def read_file(path: str):
    srv = get_services()
    try:
        content = srv["fs"].read_file(path)
        return {
            "path": path,
            "content": content,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except SecurityViolation as sec_err:
        raise HTTPException(status_code=403, detail=str(sec_err))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/file")
def write_file(req: FileSaveRequest):
    srv = get_services()
    try:
        target = srv["fs"].modify_file(req.path, req.content)
        return {
            "status": "saved",
            "path": req.path,
            "bytes": len(req.content.encode("utf-8")),
        }
    except SecurityViolation as sec_err:
        raise HTTPException(status_code=403, detail=str(sec_err))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/config")
def get_config():
    srv = get_services()
    cfg = srv["memory"].get_config()
    return {
        "provider": settings.provider,
        "model": settings.model,
        "workspace_root": str(settings.workspace_root),
        "ollama_host": settings.ollama_host,
        "has_openai_key": bool(settings.openai_api_key),
        "has_anthropic_key": bool(settings.anthropic_api_key),
        "has_gemini_key": bool(settings.gemini_api_key),
        "has_groq_key": bool(settings.groq_api_key),
        "project_config": cfg.dict(),
    }


@app.post("/config")
def update_config(req: ConfigUpdateRequest):
    if req.provider:
        settings.provider = req.provider
    if req.model is not None:
        settings.model = req.model
    if req.openai_api_key is not None:
        settings.openai_api_key = req.openai_api_key
    if req.anthropic_api_key is not None:
        settings.anthropic_api_key = req.anthropic_api_key
    if req.gemini_api_key is not None:
        settings.gemini_api_key = req.gemini_api_key
    if req.groq_api_key is not None:
        settings.groq_api_key = req.groq_api_key
    if req.ollama_host is not None:
        settings.ollama_host = req.ollama_host

    return {
        "status": "updated",
        "provider": settings.provider,
        "model": settings.model,
    }


@app.post("/chat")
def chat(payload: dict):
    message = payload.get("message", "").strip()
    context = payload.get("context", {})

    if not message:
        return {
            "reply": "Send me a message and I'll help you plan, build, and debug your project."
        }

    srv = get_services()
    full_ctx = {
        **srv["memory"].get_context_for_prompt(),
        **context,
        "project_files": srv["fs"].list_files(limit=100),
    }

    provider = ProviderFactory.get_provider()
    try:
        reply = provider.chat(message, full_ctx)
    except Exception as exc:
        reply = f"Kodra Agent received: '{message}'. Note: Provider notice: {str(exc)}"

    return {"reply": reply}


@app.get("/agents")
def list_agents():
    srv = get_services()
    return {"agents": srv["orchestrator"].list_specialists()}


@app.post("/plan")
def generate_plan(req: PlanGenerationRequest):
    task = req.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task description cannot be empty")

    srv = get_services()
    full_ctx = {
        **srv["memory"].get_context_for_prompt(),
        **req.context,
        "project_files": srv["fs"].list_files(limit=100),
    }

    if req.multi_agent:
        plan = srv["orchestrator"].plan_task_with_delegation(task, full_ctx)
    else:
        provider = ProviderFactory.get_provider()
        plan = provider.generate_plan(task, full_ctx)

    # Validate against policy before returning
    is_valid, violations = srv["policy"].validate_plan(plan)
    if not is_valid:
        plan.metadata["validation_warnings"] = violations

    return plan


@app.post("/plan/validate")
def validate_plan(plan: ExecutionPlan):
    srv = get_services()
    is_valid, violations = srv["policy"].validate_plan(plan)
    return {
        "valid": is_valid,
        "violations": violations,
    }


@app.post("/plan/execute")
def execute_plan(req: PlanExecuteRequest):
    srv = get_services()
    approved_set = set(req.approved_step_ids) if req.approved_step_ids else None
    result = srv["runner"].execute_plan(
        plan=req.plan,
        approved_step_ids=approved_set,
        auto_approve=req.auto_approve,
    )

    # Record task completion in project memory
    modified_files = [
        s.path for s in req.plan.steps
        if s.path and s.status == StepStatus.SUCCESS
    ]
    srv["memory"].record_task_history(
        task=req.plan.task,
        plan_id=req.plan.id,
        success=result.success,
        summary=result.summary,
        files_modified=modified_files,
    )

    return {
        "plan": req.plan,
        "result": result,
    }


@app.post("/plan/repair")
def repair_plan(req: PlanRepairRequest):
    srv = get_services()
    failed_step = next(
        (s for s in req.original_plan.steps if s.id == req.failed_step_id),
        None,
    )
    if not failed_step:
        raise HTTPException(status_code=404, detail="Failed step not found in plan")

    repair = srv["healer"].analyze_failure_and_create_repair_plan(
        original_plan=req.original_plan,
        failed_step=failed_step,
        error_output=req.error_output,
    )
    return repair


@app.get("/history")
def get_history():
    srv = get_services()
    cfg = srv["memory"].get_config()
    return {
        "history": cfg.history,
    }
