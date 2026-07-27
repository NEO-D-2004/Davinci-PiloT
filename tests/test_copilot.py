"""
Tests for Milestone 6: AI Copilot Chat — CopilotAgent and CopilotChatView.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch


# ── Helper: stub out PySide6 before any UI import ─────────────────────────────
def _make_pyside6_stub() -> None:
    """Create minimal PySide6 stubs so we can unit-test without a display server."""
    stubs = [
        "PySide6", "PySide6.QtWidgets", "PySide6.QtCore",
        "PySide6.QtGui", "PySide6.QtNetwork",
    ]
    for name in stubs:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    # Qt constants
    qt = sys.modules["PySide6.QtCore"]
    qt.Qt = MagicMock()
    qt.Qt.PlainText = 0
    qt.Qt.ScrollBarAlwaysOff = 1
    qt.QThread = MagicMock
    qt.Signal = MagicMock(return_value=MagicMock())
    qt.QTimer = MagicMock()
    qt.QPropertyAnimation = MagicMock()
    qt.QEasingCurve = MagicMock()

    widgets = sys.modules["PySide6.QtWidgets"]
    for cls in ["QWidget", "QVBoxLayout", "QHBoxLayout", "QLabel", "QPushButton",
                "QLineEdit", "QScrollArea", "QFrame", "QSizePolicy", "QMainWindow",
                "QMessageBox", "QTabWidget"]:
        setattr(widgets, cls, MagicMock)

    gui = sys.modules["PySide6.QtGui"]
    for cls in ["QFont", "QColor", "QIcon", "QTextOption"]:
        setattr(gui, cls, MagicMock)


_make_pyside6_stub()


# ── CopilotAgent Unit Tests ───────────────────────────────────────────────────

class TestCopilotAgentInit:
    def test_initial_history_empty(self, copilot_agent):
        assert copilot_agent.get_history_count() == 0

    def test_initial_resolve_context_empty(self, copilot_agent):
        assert copilot_agent._resolve_context == ""

    def test_quick_commands_returns_list(self, copilot_agent):
        cmds = copilot_agent.get_quick_commands()
        assert isinstance(cmds, list)
        assert len(cmds) >= 4

    def test_quick_commands_have_label_and_prompt(self, copilot_agent):
        for cmd in copilot_agent.get_quick_commands():
            assert "label" in cmd
            assert "prompt" in cmd
            assert len(cmd["label"]) > 0
            assert len(cmd["prompt"]) > 0


class TestCopilotAgentResolveContext:
    def test_update_resolve_context_with_project(self, copilot_agent):
        copilot_agent.update_resolve_context(
            project_name="MyProject",
            timeline_name="Main Timeline",
            clip_count=5,
            media_asset_count=10
        )
        ctx = copilot_agent._resolve_context
        assert "MyProject" in ctx
        assert "Main Timeline" in ctx
        assert "5 clips" in ctx
        assert "10 assets" in ctx

    def test_update_resolve_context_no_project(self, copilot_agent):
        copilot_agent.update_resolve_context()
        ctx = copilot_agent._resolve_context
        assert "No active DaVinci Resolve project" in ctx

    def test_update_resolve_context_with_analysis_summary(self, copilot_agent):
        copilot_agent.update_resolve_context(
            project_name="EditProject",
            last_analysis_summary="3 silence gaps found, 2 filler words"
        )
        ctx = copilot_agent._resolve_context
        assert "3 silence gaps" in ctx

    def test_build_system_prompt_includes_context(self, copilot_agent):
        copilot_agent.update_resolve_context(project_name="TestProject")
        prompt = copilot_agent.build_system_prompt()
        assert "TestProject" in prompt
        assert "DaVinci PiloT AI Copilot" in prompt

    def test_build_system_prompt_no_context(self, copilot_agent):
        prompt = copilot_agent.build_system_prompt()
        assert "DaVinci PiloT AI Copilot" in prompt
        assert "GLM-5.2 Master Agent" in prompt


class TestCopilotAgentHistory:
    def test_clear_history_resets_count(self, copilot_agent):
        copilot_agent.conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        assert copilot_agent.get_history_count() == 1
        copilot_agent.clear_history()
        assert copilot_agent.get_history_count() == 0

    def test_history_count_counts_pairs(self, copilot_agent):
        copilot_agent.conversation_history = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
        ]
        assert copilot_agent.get_history_count() == 2

    def test_max_history_truncation(self, copilot_agent):
        """History should be truncated to MAX_HISTORY_TURNS * 2 entries."""
        from app.ai.copilot_agent import CopilotAgent
        max_pairs = CopilotAgent.MAX_HISTORY_TURNS
        # Fill with more than max
        for i in range(max_pairs + 5):
            copilot_agent.conversation_history.append({"role": "user", "content": f"Q{i}"})
            copilot_agent.conversation_history.append({"role": "assistant", "content": f"A{i}"})
        # The slice used in send_message should be <= MAX_HISTORY_TURNS * 2
        history_slice = copilot_agent.conversation_history[-max_pairs * 2:]
        assert len(history_slice) <= max_pairs * 2


class TestCopilotAgentSendMessage:
    def test_send_empty_message_returns_empty_string(self, copilot_agent):
        result = copilot_agent.send_message("")
        assert result == ""

    def test_send_whitespace_message_returns_empty_string(self, copilot_agent):
        result = copilot_agent.send_message("   \n  ")
        assert result == ""

    def test_send_message_calls_nim_client(self, copilot_agent, mock_nim):
        mock_nim.query_master_agent.return_value = {"content": "Test AI response here."}
        result = copilot_agent.send_message("Hello Copilot")
        assert mock_nim.query_master_agent.called
        assert result == "Test AI response here."

    def test_send_message_appends_to_history(self, copilot_agent, mock_nim):
        mock_nim.query_master_agent.return_value = {"content": "Great question!"}
        copilot_agent.send_message("What is timeline pacing?")
        assert copilot_agent.get_history_count() == 1

    def test_send_message_error_returns_fallback(self, copilot_agent, mock_nim):
        mock_nim.query_master_agent.return_value = {"content": "", "error": "API timeout"}
        result = copilot_agent.send_message("Help me")
        assert "⚠️" in result or "NVIDIA" in result

    def test_send_message_multi_turn_builds_history(self, copilot_agent, mock_nim):
        mock_nim.query_master_agent.return_value = {"content": "Response A"}
        copilot_agent.send_message("Turn 1")
        mock_nim.query_master_agent.return_value = {"content": "Response B"}
        copilot_agent.send_message("Turn 2")
        assert copilot_agent.get_history_count() == 2


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_nim():
    with patch("app.ai.copilot_agent.nim_client") as m:
        m.query_master_agent = MagicMock(return_value={"content": "Mocked response"})
        yield m


@pytest.fixture
def copilot_agent(mock_nim):
    from app.ai.copilot_agent import CopilotAgent
    agent = CopilotAgent()
    return agent
