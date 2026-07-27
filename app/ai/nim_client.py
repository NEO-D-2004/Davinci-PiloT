"""
NVIDIA NIM Client Module for DaVinci PiloT.
Interacts with build.nvidia.com API endpoints using OpenAI-compatible API protocol.
Executes live HTTP requests for GLM-5.2, MiniMax M3, Nemotron ASR, and Nemotron models.
"""

import os
import json
import urllib.request
import urllib.error
import base64
from typing import Dict, Any, Optional, List
from app.settings import settings_manager
from app.services.logger_service import app_logger


class NvidiaNimClient:
    """Client wrapper for NVIDIA NIM microservices (build.nvidia.com)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or settings_manager.get("nvidia_nim_api_key", "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")
        self.base_url = base_url or settings_manager.get("nvidia_nim_base_url", "https://integrate.api.nvidia.com/v1")
        self.models = settings_manager.get("agent_matrix", {
            "master_agent": "meta/llama-3.1-70b-instruct",
            "vision_agent": "meta/llama-3.2-11b-vision-instruct",
            "speech_agent": "meta/llama-3.1-70b-instruct",
            "ocr_agent": "meta/llama-3.2-11b-vision-instruct",
            "story_agent": "meta/llama-3.1-70b-instruct",
            "editing_planner": "meta/llama-3.1-70b-instruct",
            "resolve_agent": "Deterministic DaVinci API Translator"
        })

    def is_configured(self) -> bool:
        """Check if NVIDIA NIM API Key is set."""
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    def get_model_for_role(self, role: str) -> str:
        """Return designated NVIDIA NIM model for specific agent role."""
        return self.models.get(role.lower(), self.models.get("master_agent", "meta/llama-3.1-70b-instruct"))

    def _post_chat_completion(self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.2) -> Dict[str, Any]:
        """Execute real HTTP POST request to NVIDIA NIM chat completions endpoint."""
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024,
            "top_p": 0.95
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

            app_logger.info(f"NVIDIA NIM API POST -> {url} [Model: '{model}']")
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_bytes = resp.read()
                data = json.loads(resp_bytes.decode("utf-8"))
                
                content = ""
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                
                return {
                    "status": "success",
                    "model": model,
                    "content": content,
                    "raw": data
                }
        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode("utf-8", errors="ignore")
            app_logger.error(f"NVIDIA NIM HTTP Error {http_err.code}: {error_body}")
            return {
                "status": "error",
                "model": model,
                "error": f"HTTP {http_err.code}: {http_err.reason}",
                "content": ""
            }
        except Exception as err:
            app_logger.error(f"NVIDIA NIM Connection Error: {err}")
            return {
                "status": "error",
                "model": model,
                "error": str(err),
                "content": ""
            }

    def query_speech_agent(self, prompt: str) -> Dict[str, Any]:
        """Query Speech Agent with real HTTP API call."""
        model = self.get_model_for_role("speech_agent")
        messages = [
            {"role": "system", "content": "You are Speech Analysis Agent. Transcribe and analyze speech segments, silence gaps, and timing."},
            {"role": "user", "content": prompt}
        ]
        return self._post_chat_completion(model, messages)

    def query_vision_agent(self, prompt: str, image_path: str = "") -> Dict[str, Any]:
        """Query Vision Agent (MiniMax M3 / Llama Vision) with real HTTP API call."""
        model = self.get_model_for_role("vision_agent")
        
        content_items: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]

        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                content_items.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}
                })
            except Exception as e:
                app_logger.warning(f"Could not encode keyframe image '{image_path}': {e}")

        messages = [
            {"role": "system", "content": "You are MiniMax M3 Vision Agent. Describe keyframe composition, subject motion, lighting, and visual quality."},
            {"role": "user", "content": content_items if len(content_items) > 1 else prompt}
        ]
        return self._post_chat_completion(model, messages)

    def query_master_agent(self, prompt: str) -> Dict[str, Any]:
        """Query GLM-5.2 / Master Agent with real HTTP API call."""
        model = self.get_model_for_role("master_agent")
        messages = [
            {"role": "system", "content": "You are GLM-5.2 Master Editing Agent. Synthesize speech, vision, and timeline data into prioritized smart cut proposals for DaVinci Resolve."},
            {"role": "user", "content": prompt}
        ]
        return self._post_chat_completion(model, messages)

    def get_summary(self) -> Dict[str, Any]:
        """Return client state summary."""
        return {
            "provider": "NVIDIA NIM (build.nvidia.com)",
            "configured": self.is_configured(),
            "base_url": self.base_url,
            "models": self.models
        }


# Global singleton instance
nim_client = NvidiaNimClient()
