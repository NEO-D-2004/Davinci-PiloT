"""
Unit tests for NVIDIA NIM Client and Multi-Agent Router.
"""

from app.ai import NvidiaNimClient, AgentRouter, AgentTaskRole


def test_nvidia_nim_client():
    client = NvidiaNimClient()
    assert client.get_model_for_role("master_planner") == "GLM-5.2"
    assert client.get_model_for_role("vision") == "MiniMax M3"
    assert client.get_model_for_role("reasoning") == "Nemotron-3 Ultra 550B"
    assert client.get_model_for_role("ocr") == "Nemotron OCR v2"
    assert client.get_model_for_role("asr") == "Nemotron ASR Streaming"
    assert client.get_model_for_role("embeddings") == "Nemotron Embed 1B"


def test_agent_router():
    router = AgentRouter()
    specs = router.get_agent_specs()
    
    assert specs[AgentTaskRole.MASTER_PLANNER]["model"] == "GLM-5.2"
    assert specs[AgentTaskRole.VISION]["model"] == "MiniMax M3"
    assert specs[AgentTaskRole.REASONING]["model"] == "Nemotron-3 Ultra 550B"
    assert specs[AgentTaskRole.OCR]["model"] == "Nemotron OCR v2"
    assert specs[AgentTaskRole.ASR]["model"] == "Nemotron ASR Streaming"
    assert specs[AgentTaskRole.EMBEDDINGS]["model"] == "Nemotron Embed 1B"
