"""FastAPI application for the Construction Intelligence Hub."""

from __future__ import annotations

import os
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

import requests
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.auth_service import AuthService
from backend.config import Config
from backend.cost_calculator import CostCalculator
from backend.feature_services import (
    analyze_compliance,
    analyze_insurance,
    analyze_safety_sample,
    generate_daily_report,
    generate_report,
    generate_themes,
    match_uploaded_sample,
    safety_samples,
)
from backend.guardrails import apply_output_guardrails, check_input_guardrails
from backend.llama_service import LlamaService
from backend.material_calculator import MaterialCalculator
from backend.ollama_manager import OllamaManager
from backend.prompt_manager import PromptManager
from backend.task_manager import TaskManager


APP_STARTED_AT = time.time()
ROOT_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT_DIR / "public"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

@asynccontextmanager
async def lifespan(_: FastAPI):
    threading.Thread(target=ollama_manager.start, daemon=True, name="cih-ollama-startup").start()
    yield


app = FastAPI(title="CIH API", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8555",
        "http://127.0.0.1:8555",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()
llama_service = LlamaService(config)
ollama_manager = OllamaManager(config)
auth_service = AuthService()
prompt_manager = PromptManager(config)
material_calculator = MaterialCalculator(config)
cost_calculator = CostCalculator(config)
task_manager = TaskManager()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    history: List[Dict[str, str]] = Field(default_factory=list)
    project_context: str = Field(default="", max_length=30_000)


class ProjectConfig(BaseModel):
    area: float = Field(gt=0, le=10_000_000)
    floors: int = Field(gt=0, le=200)
    house_type: str = Field(min_length=1, max_length=100)


class ReportRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    report_type: str = Field(default="Executive Summary", max_length=100)
    prepared_by: str = Field(default="", max_length=200)
    report_date: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=30_000)


class DailyReportRequest(BaseModel):
    report_date: str = Field(default="", max_length=100)
    location: str = Field(default="", max_length=200)
    weather: str = Field(default="", max_length=200)
    manpower: str = Field(default="", max_length=100)
    tasks_completed: str = Field(min_length=1, max_length=10_000)
    issues: str = Field(default="None reported.", max_length=5_000)


class ComplianceRequest(BaseModel):
    phase: str = Field(min_length=1, max_length=100)
    standard: str = Field(min_length=1, max_length=100)
    notes: str = Field(default="", max_length=30_000)


class InsuranceRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    impact: float = Field(ge=0, le=1_000_000_000_000)
    description: str = Field(min_length=1, max_length=30_000)


def require_admin(authorization: str | None) -> Dict[str, Any]:
    if not auth_service.admin_configured:
        raise HTTPException(status_code=503, detail="Administrator access is not configured on the server.")
    user = auth_service.verify_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="A valid authenticated session is required.")
    if not auth_service.is_admin(user):
        raise HTTPException(status_code=403, detail="Administrator access is required.")
    return user


def build_chat_response(request: ChatRequest) -> str:
    system_prompt = prompt_manager.get_system_prompt()
    messages = [{"role": "system", "content": system_prompt + "\n\n" + request.project_context}]
    messages.extend(
        {"role": message.get("role", "user"), "content": str(message.get("content", ""))}
        for message in request.history[-config.MAX_CONVERSATION_MESSAGES :]
        if message.get("role") in {"user", "assistant"}
    )
    messages.append({"role": "user", "content": request.message})
    response = "".join(llama_service.chat(messages)).strip()
    if not response:
        raise RuntimeError("Ollama returned an empty response.")
    return apply_output_guardrails(response)


@app.get("/api/health")
def health() -> Dict[str, Any]:
    ollama = ollama_manager.status()
    return {
        "status": "ready" if ollama["state"] == "ready" else "degraded",
        "version": app.version,
        "uptime_seconds": round(time.time() - APP_STARTED_AT, 1),
        "ollama": ollama,
        "tasks": task_manager.stats(),
        "features": {
            "reporting": True,
            "theme_visualizer": True,
            "safety_dataset_demo": bool(safety_samples(1)),
            "custom_ppe_model": bool(os.getenv("PPE_MODEL_PATH")),
            "compliance": True,
            "insurance": True,
            "admin": auth_service.admin_configured,
            "user_metrics": auth_service.user_metrics_configured,
        },
    }


@app.get("/api/ollama/status")
def ollama_status() -> Dict[str, Any]:
    return ollama_manager.status()


@app.post("/api/chat")
def chat_endpoint(request: ChatRequest) -> Dict[str, str]:
    if not check_input_guardrails(request.message):
        refusal = (
            "Sorry! I am the Construction Intelligence Hub assistant and can only help "
            "with construction planning, estimating, design, engineering, safety, "
            "compliance, insurance risk, and project reporting questions."
        )
        return task_manager.completed("chat", refusal)
    return task_manager.submit("chat", lambda: build_chat_response(request))


@app.get("/api/tasks/{task_id}")
@app.get("/api/chat/status/{task_id}")
def get_task_status(task_id: str) -> Dict[str, Any]:
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or expired.")
    return task


@app.post("/api/calculate")
def calculate_endpoint(project: ProjectConfig) -> Dict[str, Any]:
    try:
        materials = material_calculator.calculate_all(project.area, project.floors, project.house_type)
        costs = cost_calculator.calculate_costs(project.area, project.floors, project.house_type, materials)
        return {"materials": materials, "costs": costs, "total_cost": cost_calculator.get_total_cost(costs)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/weather")
def get_weather(city: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENWEATHERMAP_API_KEY is not configured.")
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "units": "metric", "appid": api_key},
            timeout=10,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Weather provider unavailable: {exc}") from exc


@app.post("/api/reports/generate")
def report_endpoint(request: ReportRequest) -> Dict[str, str]:
    data = request.model_dump()
    return task_manager.submit("report", lambda: generate_report(llama_service, data))


@app.post("/api/daily-report")
def daily_report_endpoint(request: DailyReportRequest) -> Dict[str, str]:
    data = request.model_dump()
    return task_manager.submit("daily_report", lambda: generate_daily_report(llama_service, data))



@app.post("/api/compliance/analyze")
def compliance_endpoint(request: ComplianceRequest) -> Dict[str, str]:
    data = request.model_dump()
    return task_manager.submit("compliance", lambda: analyze_compliance(llama_service, data))


@app.post("/api/insurance/analyze")
def insurance_endpoint(request: InsuranceRequest) -> Dict[str, str]:
    data = request.model_dump()
    return task_manager.submit("insurance", lambda: analyze_insurance(llama_service, data))


@app.post("/api/theme-generator")
async def theme_generator_endpoint(
    file: UploadFile = File(...),
    theme_prompt: str = Form(default=""),
) -> Dict[str, Any]:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MB upload limit.")
    try:
        return {"status": "success", "themes": generate_themes(llama_service, content, theme_prompt)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/safety/images")
def safety_images_endpoint(limit: int = 12) -> List[str]:
    return safety_samples(limit)


@app.get("/api/safety/detect/{filename}")
def safety_sample_endpoint(filename: str) -> Dict[str, Any]:
    try:
        return analyze_safety_sample(llama_service, filename)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/safety/upload")
async def safety_upload_endpoint(file: UploadFile = File(...)) -> Dict[str, Any]:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MB upload limit.")
    sample = match_uploaded_sample(file.filename or "", content)
    if sample:
        return analyze_safety_sample(llama_service, sample)
    raise HTTPException(
        status_code=503,
        detail=(
            "Custom-image PPE inference is unavailable because PPE_MODEL_PATH is not configured. "
            "Use a labelled dataset sample or install a trained PPE detector. No simulated detection was returned."
        ),
    )


@app.get("/api/auth/me")
def auth_me(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    user = auth_service.verify_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="A valid authenticated session is required.")
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "is_admin": auth_service.is_admin(user),
        "admin_configured": auth_service.admin_configured,
    }


@app.get("/api/admin/metrics")
def admin_metrics(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    user = require_admin(authorization)
    try:
        users = auth_service.list_user_metrics()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Could not load Supabase user metrics: {exc}") from exc
    return {
        "administrator": user.get("email"),
        "users": users,
        "ollama": ollama_manager.status(),
        "tasks": task_manager.stats(),
        "uptime_seconds": round(time.time() - APP_STARTED_AT, 1),
    }


@app.post("/api/admin/ollama/start")
def admin_start_ollama(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    require_admin(authorization)
    result = ollama_manager.start()
    if result["state"] == "failed":
        raise HTTPException(status_code=503, detail=result.get("error", "Ollama failed to start."))
    return result


@app.post("/api/admin/ollama/restart")
def admin_restart_ollama(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    require_admin(authorization)
    result = ollama_manager.restart()
    if result["state"] == "failed":
        raise HTTPException(status_code=503, detail=result.get("error", "Ollama failed to restart."))
    return result


@app.post("/api/restart-ollama")
def legacy_restart_ollama(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    return admin_restart_ollama(authorization)


PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
(PUBLIC_DIR / "generated_themes").mkdir(parents=True, exist_ok=True)
app.mount("/generated_themes", StaticFiles(directory=PUBLIC_DIR / "generated_themes"), name="generated_themes")
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8555, reload=False)