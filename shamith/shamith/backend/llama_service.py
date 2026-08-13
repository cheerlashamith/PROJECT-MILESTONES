"""
Llama Service – Ollama Communication Layer
==========================================
Handles all communication with the Ollama API: health checks,
model availability, streaming chat, and single-shot generation.
"""

import os
import time
import requests
from backend.config import Config


class LlamaService:
    """Manages communication with Ollama/OpenAI for inference."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.host = self.config.OLLAMA_HOST
        self.model = self.config.MODEL_NAME
        self.api_key = os.environ.get("OPENAI_API_KEY", "")

    # ── Health Checks ────────────────────────────────────────────────

    def check_ollama_running(self) -> bool:
        """Ping the Engine API to check if the server is running."""
        if "openai" in self.host.lower():
            return True
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            return resp.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def check_model_available(self, model_name: str = None) -> bool:
        """Check if the specified model is pulled and available."""
        model_name = model_name or self.model
        if "openai" in self.host.lower():
            return True
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                for m in models:
                    name = m.get("name", "")
                    if model_name in name or name.startswith(model_name):
                        return True
            return False
        except (requests.ConnectionError, requests.Timeout):
            return False

    def get_available_models(self) -> list:
        """Return list of all models available in Engine."""
        if "openai" in self.host.lower():
            return [self.model]
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return [m.get("name", "") for m in models]
            return []
        except (requests.ConnectionError, requests.Timeout):
            return []

    def get_status(self) -> dict:
        """Get comprehensive status of Ollama and the configured model."""
        ollama_running = self.check_ollama_running()
        model_available = self.check_model_available() if ollama_running else False
        available_models = self.get_available_models() if ollama_running else []

        return {
            "ollama_running": ollama_running,
            "model_available": model_available,
            "model_name": self.model,
            "available_models": available_models,
            "host": self.host,
        }

    # ── Chat (Streaming) ────────────────────────────────────────────

    def chat(self, messages: list, temperature: float = None, max_tokens: int = None):
        """
        Send a chat request to Ollama and yield response tokens as they stream in.

        Args:
            messages: List of dicts with 'role' and 'content' keys.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.

        Yields:
            str: Each token/chunk of the response as it arrives.
        """
        temperature = temperature or self.config.TEMPERATURE
        max_tokens = max_tokens or self.config.MAX_TOKENS

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = requests.post(
                f"{self.host}/v1/chat/completions",
                json=payload,
                headers=headers,
                stream=True,
                timeout=self.config.TIMEOUT,
            )
            resp.raise_for_status()

            for line in resp.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        try:
                            data = json.loads(line[6:])
                            token = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, IndexError, TypeError, AttributeError):
                            continue

        except requests.ConnectionError:
            yield "\n\n⚠️ **Connection Error**: Could not connect to AI Engine. Please make sure LM Studio or Ollama is running."
        except requests.Timeout:
            yield "\n\n⚠️ **Timeout**: The AI took too long to respond. Try a shorter question or check system resources."
        except requests.HTTPError as e:
            yield f"\n\n⚠️ **Error**: {str(e)}"
        except Exception as e:
            yield f"\n\n⚠️ **Unexpected Error**: {str(e)}"

    # ── Generate (Single-shot) ──────────────────────────────────────

    def generate(self, prompt: str, system: str = None, temperature: float = None) -> str:
        """
        Send a single-shot generation request (non-streaming).
        Used for material analysis, cost optimization, project insights, etc.

        Args:
            prompt: The user prompt / instruction.
            system: Optional system prompt override.
            temperature: Override default temperature.

        Returns:
            str: The complete AI response text.
        """
        temperature = temperature or self.config.TEMPERATURE
        system = system or self.config.SYSTEM_PROMPT
        
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": self.config.MAX_TOKENS,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            start_time = time.time()
            resp = requests.post(
                f"{self.host}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.config.TIMEOUT,
            )
            resp.raise_for_status()
            elapsed = time.time() - start_time

            data = resp.json()
            response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return response_text

        except requests.ConnectionError:
            return "⚠️ **Connection Error**: Could not connect to AI Engine. Please make sure LM Studio or Ollama is running."
        except requests.Timeout:
            return "⚠️ **Timeout**: The AI took too long to respond. Try simplifying your request."
        except requests.HTTPError as e:
            return f"⚠️ **Error**: {str(e)}"
        except Exception as e:
            return f"⚠️ **Unexpected Error**: {str(e)}"
