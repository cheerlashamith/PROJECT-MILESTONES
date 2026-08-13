"""Safe local Ollama process discovery, startup, restart, and status checks."""

from __future__ import annotations

import os
import shutil
# Required for fixed local Ollama process controls.
import subprocess  # nosec B404
import time
from pathlib import Path
from typing import Any, Dict

import requests

from backend.config import Config


class OllamaManager:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    def status(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.config.OLLAMA_HOST}/api/tags", timeout=3)
            response.raise_for_status()
            models = [m.get("name", "") for m in response.json().get("models", [])]
            target = self.config.MODEL_NAME
            model_available = any(
                name == target or name == f"{target}:latest" or name.startswith(f"{target}:")
                for name in models
            )
            return {
                "state": "ready" if model_available else "model_missing",
                "running": True,
                "model_available": model_available,
                "model": target,
                "models": models,
                "host": self.config.OLLAMA_HOST,
            }
        except (requests.RequestException, ValueError) as exc:
            return {
                "state": "offline",
                "running": False,
                "model_available": False,
                "model": self.config.MODEL_NAME,
                "models": [],
                "host": self.config.OLLAMA_HOST,
                "error": str(exc),
            }

    def executable(self) -> str | None:
        configured = os.getenv("OLLAMA_PATH", "").strip()
        candidates = [configured, shutil.which("ollama")]
        if os.name == "nt":
            local_app_data = os.getenv("LOCALAPPDATA", "")
            if local_app_data:
                candidates.append(str(Path(local_app_data) / "Programs" / "Ollama" / "ollama.exe"))
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return str(Path(candidate))
        return None

    def start(self, timeout: float = 20.0) -> Dict[str, Any]:
        current = self.status()
        if current["running"]:
            return current

        executable = self.executable()
        if not executable:
            return {**current, "state": "failed", "error": "Ollama executable was not found."}

        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            # The executable is resolved and validated as a local file.
            subprocess.Popen(  # nosec B603
                [executable, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
        except OSError as exc:
            return {**current, "state": "failed", "error": f"Could not start Ollama: {exc}"}

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            time.sleep(0.5)
            current = self.status()
            if current["running"]:
                return current
        return {**self.status(), "state": "failed", "error": "Ollama did not become ready before timeout."}

    def restart(self) -> Dict[str, Any]:
        """Request a graceful Windows process stop, then start and verify Ollama."""
        if os.name == "nt" and self.status()["running"]:
            taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
            # Absolute system executable with fixed arguments.
            subprocess.run(  # nosec B603
                [str(taskkill), "/F", "/IM", "ollama.exe", "/T"],
                capture_output=True,
                timeout=10,
                check=False,
            )
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline and self.status()["running"]:
                time.sleep(0.5)
            if self.status()["running"]:
                return {**self.status(), "state": "failed", "error": "Ollama did not stop, so it was not restarted."}
        return self.start()