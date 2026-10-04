"""Logging utilities for the Voice Assistant with robust Windows console support."""

import sys
import logging

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "assistant": "bold magenta",
    "user": "bold green",
    "system": "bold blue",
    "highlight": "bold yellow"
})

# Use safe terminal encoding
console = Console(theme=custom_theme, legacy_windows=False)

# Standard logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("VoiceAssistant")
# Suppress noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)
logging.getLogger("comtypes").setLevel(logging.WARNING)


def print_banner(assistant_name: str, mode: str = "voice") -> None:
    """Print an attractive startup banner."""
    console.print()
    console.rule(f"[assistant]* {assistant_name.upper()} AI VOICE ASSISTANT *[/assistant]", style="magenta")
    console.print(f"[info]Mode:[/info] [bold]{mode.upper()}[/bold] | [info]Engine:[/info] SpeechRecognition + pyttsx3 + Gemini AI", justify="center")
    console.print("[dim]Local Desktop Controller - Windows Optimized - Production Ready[/dim]", justify="center")
    console.rule(style="magenta")
    console.print()


def log_user(text: str) -> None:
    """Log transcribed user speech or text input."""
    console.print(f"[user][You]:[/user] {text}")


def log_assistant(text: str) -> None:
    """Log assistant spoken output or reply."""
    console.print(f"[assistant][{assistant_name_label()}]:[/assistant] {text}")


def log_system(text: str) -> None:
    """Log system operations or hardware updates."""
    console.print(f"[system][System]:[/system] {text}")


def log_warning(text: str) -> None:
    """Log a warning message."""
    console.print(f"[warning][Warning]:[/warning] {text}")


def log_error(text: str) -> None:
    """Log an error message."""
    console.print(f"[error][Error]:[/error] {text}")


def log_info(text: str) -> None:
    """Log an informational message."""
    console.print(f"[info][Info]:[/info] {text}")


def assistant_name_label() -> str:
    """Helper to get current assistant name."""
    try:
        from src.config import Config
        return Config.ASSISTANT_NAME
    except Exception:
        return "Assistant"
