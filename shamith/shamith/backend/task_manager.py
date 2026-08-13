"""Thread-safe background task storage for long-running local AI requests."""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Callable, Dict


class TaskManager:
    """Run callables in daemon threads and expose their lifecycle safely."""

    def __init__(self, retention_seconds: int = 3600):
        self.retention_seconds = retention_seconds
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def submit(self, task_type: str, operation: Callable[[], Any]) -> Dict[str, str]:
        self.cleanup()
        task_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "type": task_type,
                "status": "generating",
                "created_at": time.time(),
                "updated_at": time.time(),
            }

        def runner() -> None:
            try:
                result = operation()
                with self._lock:
                    task = self._tasks[task_id]
                    task["result"] = result
                    # Preserve the original chat response contract.
                    if isinstance(result, str):
                        task["response"] = result
                    task["status"] = "completed"
                    task["updated_at"] = time.time()
            except Exception as exc:  # The API returns the sanitized message.
                with self._lock:
                    task = self._tasks[task_id]
                    task["status"] = "error"
                    task["error"] = str(exc)
                    task["updated_at"] = time.time()

        threading.Thread(target=runner, daemon=True, name=f"cih-{task_type}-{task_id[:8]}").start()
        return {"task_id": task_id, "status": "generating"}

    def completed(self, task_type: str, result: Any) -> Dict[str, Any]:
        """Create an already-completed task (used for guardrail refusals)."""
        task_id = str(uuid.uuid4())
        now = time.time()
        task = {
            "task_id": task_id,
            "type": task_type,
            "status": "completed",
            "result": result,
            "created_at": now,
            "updated_at": now,
        }
        if isinstance(result, str):
            task["response"] = result
        with self._lock:
            self._tasks[task_id] = task
        return {"task_id": task_id, "status": "completed"}

    def get(self, task_id: str) -> Dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task else None

    def stats(self) -> Dict[str, int]:
        with self._lock:
            values = list(self._tasks.values())
        return {
            "total": len(values),
            "generating": sum(t["status"] == "generating" for t in values),
            "completed": sum(t["status"] == "completed" for t in values),
            "error": sum(t["status"] == "error" for t in values),
        }

    def cleanup(self) -> None:
        cutoff = time.time() - self.retention_seconds
        with self._lock:
            expired = [
                task_id
                for task_id, task in self._tasks.items()
                if task["status"] != "generating" and task["updated_at"] < cutoff
            ]
            for task_id in expired:
                self._tasks.pop(task_id, None)