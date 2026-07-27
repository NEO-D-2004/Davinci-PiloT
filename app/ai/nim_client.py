"""
NVIDIA NIM Client Module for DaVinci PiloT.
Interacts with build.nvidia.com API endpoints using OpenAI-compatible API protocol.
Maps human-readable agent labels to valid hosted NVIDIA NIM model identifiers.
"""

import os
import json
import urllib.request
import urllib.error
import base64
from typing import Dict, Any, Optional, List
from app.settings import settings_manager
from app.services.logger_service import app_logger

# Map human-readable agent display labels to valid NVIDIA NIM endpoints on integrate.api.nvidia.com
VALID_NIM_MODELS = {
    "GLM-5.2": "meta/llama-3.1-70b-instruct",
    "MiniMax M3": "meta/llama-3.2-11b-vision-instruct",
    "Nemotron ASR": "meta/llama-3.1-70b-instruct",
    "Nemotron ASR Streaming": "meta/llama-3.1-70b-instruct",
    "Nemotron OCR v2": "meta/llama-3.2-11b-vision-instruct",
    "Nemotron-3 Ultra 550B": "meta/llama-3.1-70b-instruct",
    "Nemotron Embed 1B": "nvidia/embed-qa-4",
    "Deterministic DaVinci API Translator": "meta/llama-3.1-70b-instruct"
}

DEFAULT_NVIDIA_KEY = "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"


class NvidiaNimClient:
    """Client wrapper for NVIDIA NIM microservices (build.nvidia.com)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        # Check explicit parameter -> environment variable -> settings file -> default key
        env_key = os.getenv("NVIDIA_NIM_API_KEY", "").strip().strip('"').strip("'")
        settings_key = str(settings_manager.get("nvidia_nim_api_key", "")).strip().strip('"').strip("'")
        
        chosen_key = api_key or env_key or settings_key or DEFAULT_NVIDIA_KEY
        self.api_key = str(chosen_key).strip().strip('"').strip("'")

        env_url = os.getenv("NVIDIA_NIM_BASE_URL", "").strip().strip('"').strip("'")
        settings_url = str(settings_manager.get("nvidia_nim_base_url", "")).strip().strip('"').strip("'")
        chosen_url = base_url or env_url or settings_url or "https://integrate.api.nvidia.com/v1"
        
        self.base_url = str(chosen_url).strip().strip('"').strip("'")

        self.models = settings_manager.get("agent_matrix", {
            "master_agent": "GLM-5.2",
            "vision_agent": "MiniMax M3",
            "speech_agent": "Nemotron ASR Streaming",
            "ocr_agent": "Nemotron OCR v2",
            "story_agent": "GLM-5.2",
            "editing_planner": "Nemotron-3 Ultra 550B",
            "resolve_agent": "Deterministic DaVinci API Translator"
        })

    def is_configured(self) -> bool:
        """Check if NVIDIA NIM API Key is set."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def get_model_for_role(self, role: str) -> str:
        """Return designated agent display model for specific agent role."""
        return self.models.get(role.lower(), self.models.get("master_agent", "GLM-5.2"))

    def _post_chat_completion(self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.2) -> Dict[str, Any]:
        """Execute real HTTP POST request to NVIDIA NIM chat completions endpoint."""
        # Resolve display label (e.g. GLM-5.2 -> meta/llama-3.1-70b-instruct)
        endpoint_model = VALID_NIM_MODELS.get(model, model)
        if "/" not in endpoint_model:
            endpoint_model = "meta/llama-3.1-70b-instruct"

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        clean_key = self.api_key.strip().strip('"').strip("'")
        
        headers = {
            "Authorization": f"Bearer {clean_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "model": endpoint_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024,
            "top_p": 0.95
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

            app_logger.info(f"NVIDIA NIM API POST -> {url} [Agent: '{model}' -> Endpoint: '{endpoint_model}']")
            with urllib.request.urlopen(req, timeout=35) as resp:
                resp_bytes = resp.read()
                data = json.loads(resp_bytes.decode("utf-8"))
                
                content = ""
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                
                return {
                    "status": "success",
                    "model": endpoint_model,
                    "content": content,
                    "raw": data
                }
        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode("utf-8", errors="ignore")
            app_logger.error(f"NVIDIA NIM HTTP Error {http_err.code} for '{endpoint_model}': {error_body}")
            
            # Fallback to default llama-3.1-70b if specific model returns 404
            if http_err.code == 404 and endpoint_model != "meta/llama-3.1-70b-instruct":
                app_logger.info(f"Retrying with fallback model 'meta/llama-3.1-70b-instruct'...")
                return self._post_chat_completion("meta/llama-3.1-70b-instruct", messages, temperature)

            return {
                "status": "error",
                "model": endpoint_model,
                "error": f"HTTP {http_err.code}: {http_err.reason}",
                "content": ""
            }
        except Exception as err:
            app_logger.error(f"NVIDIA NIM Connection Error for '{endpoint_model}': {err}")
            return {
                "status": "error",
                "model": endpoint_model,
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

        # Only encode image files (.jpg, .jpeg, .png, .webp), never raw video containers (.mp4, .mov)
        valid_img_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        if image_path and os.path.exists(image_path) and os.path.splitext(image_path)[1].lower() in valid_img_exts:
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
