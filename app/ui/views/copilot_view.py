"""
AI Copilot Chat View — Milestone 6 of DaVinci PiloT.
Premium dark glassmorphism chat UI with context-aware GLM-5.2 Master Agent responses,
multi-turn conversation history, typing indicator, and quick command chips.
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QTextOption
from app.ai.copilot_agent import CopilotAgent
from app.models.resolve_models import ResolveState
from app.services.logger_service import app_logger


class CopilotWorkerThread(QThread):
    """Background thread for non-blocking NVIDIA NIM GLM-5.2 API calls."""
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, agent: CopilotAgent, user_text: str) -> None:
        super().__init__()
        self._agent = agent
        self._user_text = user_text

    def run(self) -> None:
        try:
            response = self._agent.send_message(self._user_text)
            self.response_ready.emit(response)
        except Exception as e:
            app_logger.error(f"CopilotWorkerThread error: {e}")
            self.error_occurred.emit(str(e))


class MessageBubble(QFrame):
    """A styled chat message bubble widget for both user and AI messages."""

    def __init__(self, text: str, role: str = "user", agent_label: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.role = role

        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 4, 12, 4)
        outer.setSpacing(0)

        # Inner bubble widget
        bubble = QFrame()
        bubble.setWordWrap = True

        if role == "user":
            bubble.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #313244, stop:1 #45475A);
                    border-radius: 14px 14px 4px 14px;
                    border: 1px solid #585B70;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1E1E2E, stop:1 #181825);
                    border-radius: 14px 14px 14px 4px;
                    border: 1px solid #313244;
                }
            """)

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(4)

        # Agent label for AI messages
        if role == "assistant" and agent_label:
            lbl_agent = QLabel(f"🤖 {agent_label}")
            lbl_agent.setFont(QFont("Segoe UI", 8, QFont.Bold))
            lbl_agent.setStyleSheet("color: #A6E3A1; background: transparent; border: none;")
            bubble_layout.addWidget(lbl_agent)

        # Message text
        msg_label = QLabel(text)
        msg_label.setWordWrap(True)
        msg_label.setTextFormat(Qt.PlainText)
        msg_label.setFont(QFont("Segoe UI", 11))
        msg_label.setStyleSheet(
            "color: #CDD6F4; background: transparent; border: none;"
            if role == "assistant"
            else "color: #CDD6F4; background: transparent; border: none;"
        )
        msg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        msg_label.setMaximumWidth(580)
        bubble_layout.addWidget(msg_label)

        bubble.setMaximumWidth(620)

        if role == "user":
            outer.addStretch(1)
            outer.addWidget(bubble)
        else:
            outer.addWidget(bubble)
            outer.addStretch(1)


class TypingIndicator(QFrame):
    """Animated typing indicator shown while waiting for AI response."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._dots = 0
        self.setStyleSheet("""
            QFrame {
                background: #1E1E2E;
                border-radius: 14px 14px 14px 4px;
                border: 1px solid #313244;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        lbl = QLabel("🤖 GLM-5.2 is thinking")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setStyleSheet("color: #A6E3A1; background: transparent; border: none;")
        layout.addWidget(lbl)

        self._dots_lbl = QLabel("•••")
        self._dots_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._dots_lbl.setStyleSheet("color: #89B4FA; background: transparent; border: none;")
        layout.addWidget(self._dots_lbl)
        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(400)

    def _tick(self) -> None:
        self._dots = (self._dots + 1) % 4
        self._dots_lbl.setText("•" * self._dots if self._dots > 0 else "")

    def stop(self) -> None:
        self._timer.stop()


class CopilotChatView(QWidget):
    """
    Main AI Copilot Chat View — Milestone 6.
    Context-aware conversational interface powered by NVIDIA NIM GLM-5.2 Master Agent.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._agent = CopilotAgent()
        self._worker: Optional[CopilotWorkerThread] = None
        self._typing_widget: Optional[TypingIndicator] = None
        self._resolve_state: Optional[ResolveState] = None
        self._init_ui()
        self._show_welcome_message()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header Bar ────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1E1E2E, stop:1 #181825);
                border-bottom: 1px solid #313244;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)

        title_icon = QLabel("🤖")
        title_icon.setFont(QFont("Segoe UI", 24))
        title_icon.setStyleSheet("border: none; background: transparent;")
        header_layout.addWidget(title_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_lbl = QLabel("AI Copilot")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #CDD6F4; border: none; background: transparent;")
        title_col.addWidget(title_lbl)

        self._context_lbl = QLabel("Waiting for DaVinci Resolve connection...")
        self._context_lbl.setFont(QFont("Segoe UI", 9))
        self._context_lbl.setStyleSheet("color: #6C7086; border: none; background: transparent;")
        title_col.addWidget(self._context_lbl)

        header_layout.addLayout(title_col)
        header_layout.addStretch()

        self._clear_btn = QPushButton("🗑 Clear Chat")
        self._clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #585B70;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                color: #F38BA8;
                border-color: #F38BA8;
            }
        """)
        self._clear_btn.clicked.connect(self._clear_chat)
        header_layout.addWidget(self._clear_btn)

        main_layout.addWidget(header)

        # ── Message Feed (scroll area) ────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea { background: #11111B; border: none; }
            QScrollBar:vertical {
                background: #181825; width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #45475A; border-radius: 3px; min-height: 24px;
            }
        """)

        self._feed_widget = QWidget()
        self._feed_widget.setStyleSheet("background: #11111B;")
        self._feed_layout = QVBoxLayout(self._feed_widget)
        self._feed_layout.setContentsMargins(8, 12, 8, 12)
        self._feed_layout.setSpacing(8)
        self._feed_layout.addStretch()

        self._scroll.setWidget(self._feed_widget)
        main_layout.addWidget(self._scroll, 1)

        # ── Quick Command Chips ──────────────────────────────────────────────
        chips_frame = QFrame()
        chips_frame.setStyleSheet("QFrame { background: #181825; border-top: 1px solid #1E1E2E; border-bottom: none; }")
        chips_frame.setFixedHeight(52)
        chips_layout = QHBoxLayout(chips_frame)
        chips_layout.setContentsMargins(16, 8, 16, 8)
        chips_layout.setSpacing(8)

        for cmd in self._agent.get_quick_commands()[:4]:
            btn = QPushButton(cmd["label"])
            btn.setStyleSheet("""
                QPushButton {
                    background: #1E1E2E;
                    color: #89B4FA;
                    border: 1px solid #313244;
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-size: 10px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #313244;
                    border-color: #89B4FA;
                    color: #CDD6F4;
                }
            """)
            prompt = cmd["prompt"]
            btn.clicked.connect(lambda checked=False, p=prompt: self._quick_command(p))
            chips_layout.addWidget(btn)

        chips_layout.addStretch()
        main_layout.addWidget(chips_frame)

        # ── Input Bar ────────────────────────────────────────────────────────
        input_frame = QFrame()
        input_frame.setFixedHeight(64)
        input_frame.setStyleSheet("""
            QFrame {
                background: #181825;
                border-top: 1px solid #313244;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 10, 16, 10)
        input_layout.setSpacing(12)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask your AI Copilot anything about your timeline, clips, or edits…")
        self._input.setFont(QFont("Segoe UI", 12))
        self._input.setStyleSheet("""
            QLineEdit {
                background: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 20px;
                padding: 8px 18px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #89B4FA;
                background: #242438;
            }
        """)
        self._input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self._input, 1)

        self._send_btn = QPushButton("Send ➤")
        self._send_btn.setFixedSize(90, 40)
        self._send_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #89B4FA, stop:1 #74C7EC);
                color: #11111B;
                border-radius: 20px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #B4BEFE, stop:1 #89B4FA);
            }
            QPushButton:disabled {
                background: #45475A;
                color: #6C7086;
            }
        """)
        self._send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self._send_btn)

        main_layout.addWidget(input_frame)

    def _show_welcome_message(self) -> None:
        """Display the initial AI Copilot welcome message."""
        welcome = (
            "Hello! I'm your DaVinci PiloT AI Copilot, powered by the GLM-5.2 Master Agent "
            "on NVIDIA NIM.\n\n"
            "I have full awareness of your active DaVinci Resolve project, timeline, and media pool. "
            "You can ask me anything about:\n"
            "• Editing decisions & smart cuts\n"
            "• Timeline optimization & pacing\n"
            "• Silence & filler word removal\n"
            "• Color grading & audio cleanup tips\n"
            "• DaVinci Resolve workflow guidance\n\n"
            "Connect DaVinci Resolve via the Bridge to unlock full context-aware assistance!"
        )
        self._append_ai_message(welcome)

    def update_resolve_state(self, state: ResolveState) -> None:
        """Sync current DaVinci Resolve context into CopilotAgent."""
        if not state:
            return

        self._resolve_state = state
        project_name = ""
        timeline_name = ""
        clip_count = 0
        media_count = 0

        if state.is_connected:
            if hasattr(state, "project") and state.project:
                project_name = state.project.name or ""
            if state.timeline_structure:
                timeline_name = state.timeline_structure.timeline_name or ""
                clip_count = len(state.timeline_structure.get_all_clips()) if hasattr(state.timeline_structure, "get_all_clips") else 0
            if state.media_pool_structure:
                assets = state.media_pool_structure.get_all_assets() if hasattr(state.media_pool_structure, "get_all_assets") else []
                media_count = len(assets)

            self._context_lbl.setText(
                f"✅ Connected — Project: '{project_name}' | Timeline: '{timeline_name}' ({clip_count} clips) | {media_count} media assets"
            )
            self._context_lbl.setStyleSheet("color: #A6E3A1; border: none; background: transparent;")
        else:
            self._context_lbl.setText("⚠️ DaVinci Resolve not connected — Run DaVinciPiloT_Bridge from Workspace → Scripts")
            self._context_lbl.setStyleSheet("color: #F9E2AF; border: none; background: transparent;")

        self._agent.update_resolve_context(
            project_name=project_name,
            timeline_name=timeline_name,
            clip_count=clip_count,
            media_asset_count=media_count
        )

    def _append_user_message(self, text: str) -> None:
        """Add a user message bubble to the feed."""
        bubble = MessageBubble(text, role="user")
        self._feed_layout.insertWidget(self._feed_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def _append_ai_message(self, text: str) -> None:
        """Add an AI response bubble to the feed."""
        bubble = MessageBubble(text, role="assistant", agent_label="GLM-5.2 Master Agent")
        self._feed_layout.insertWidget(self._feed_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def _show_typing(self) -> None:
        """Display the animated typing indicator."""
        if self._typing_widget is not None:
            return
        self._typing_widget = TypingIndicator()
        container = QHBoxLayout()
        container.setContentsMargins(12, 4, 12, 4)
        container.addWidget(self._typing_widget)
        container.addStretch()

        wrapper = QWidget()
        wrapper.setLayout(container)
        wrapper.setStyleSheet("background: #11111B;")
        self._feed_layout.insertWidget(self._feed_layout.count() - 1, wrapper)
        self._scroll_to_bottom()

    def _hide_typing(self) -> None:
        """Remove the typing indicator widget."""
        if self._typing_widget is not None:
            self._typing_widget.stop()
            parent = self._typing_widget.parent()
            if parent and parent != self:
                parent.setParent(None)
                parent.deleteLater()
            self._typing_widget = None

    def _scroll_to_bottom(self) -> None:
        """Scroll the message feed to the latest message."""
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def _send_message(self) -> None:
        """Handle send button / Enter key — dispatch user message to CopilotAgent."""
        text = self._input.text().strip()
        if not text or self._worker is not None:
            return

        self._input.clear()
        self._input.setEnabled(False)
        self._send_btn.setEnabled(False)

        self._append_user_message(text)
        self._show_typing()

        self._worker = CopilotWorkerThread(self._agent, text)
        self._worker.response_ready.connect(self._on_response_ready)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_response_ready(self, response_text: str) -> None:
        """Handle successful AI response — append bubble to feed."""
        self._hide_typing()
        self._append_ai_message(response_text)

    def _on_error(self, error_msg: str) -> None:
        """Handle worker error — show user-friendly message."""
        self._hide_typing()
        self._append_ai_message(f"⚠️ Connection error: {error_msg}\n\nPlease check your NVIDIA NIM API key and internet connection.")

    def _on_worker_finished(self) -> None:
        """Re-enable input after worker completes."""
        self._worker = None
        self._input.setEnabled(True)
        self._send_btn.setEnabled(True)
        self._input.setFocus()

    def _quick_command(self, prompt: str) -> None:
        """Pre-fill input with quick command and send immediately."""
        if self._worker is not None:
            return
        self._input.setText(prompt)
        self._send_message()

    def _clear_chat(self) -> None:
        """Clear all chat messages and reset conversation history."""
        # Remove all message bubbles (except the stretch at end)
        while self._feed_layout.count() > 1:
            item = self._feed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._agent.clear_history()
        self._show_welcome_message()
