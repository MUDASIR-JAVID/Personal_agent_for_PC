"""Configuration management for the Desktop Voice Assistant."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load environment variables from .env if present
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


class Config:
    """Application configuration parameters."""

    # Project Root
    ROOT_DIR: Path = PROJECT_ROOT

    # Gemini AI
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # Assistant Identity
    ASSISTANT_NAME: str = os.getenv("ASSISTANT_NAME", "Astra")
    _raw_wake_words: str = os.getenv("WAKE_WORDS", "astra,hey astra")
    WAKE_WORDS: List[str] = [w.strip().lower() for w in _raw_wake_words.split(",") if w.strip()]

    # Speech Synthesizer (pyttsx3)
    SPEECH_RATE: int = int(os.getenv("SPEECH_RATE", "180"))
    SPEECH_VOLUME: float = float(os.getenv("SPEECH_VOLUME", "0.9"))
    VOICE_INDEX: Optional[int] = (
        int(os.getenv("VOICE_INDEX")) if os.getenv("VOICE_INDEX") and os.getenv("VOICE_INDEX").isdigit() else 1
    )

    # Speech Recognizer
    MICROPHONE_INDEX: Optional[int] = (
        int(os.getenv("MICROPHONE_INDEX")) if os.getenv("MICROPHONE_INDEX") and os.getenv("MICROPHONE_INDEX").isdigit() else None
    )
    AMBIENT_ADJUST_DURATION: float = float(os.getenv("AMBIENT_ADJUST_DURATION", "1.0"))
    ENERGY_THRESHOLD: int = int(os.getenv("ENERGY_THRESHOLD", "300"))
    PAUSE_THRESHOLD: float = float(os.getenv("PAUSE_THRESHOLD", "0.8"))
    PHRASE_TIME_LIMIT: int = int(os.getenv("PHRASE_TIME_LIMIT", "10"))

    # Notes Directory
    _raw_notes_dir = os.getenv("NOTES_DIR", "data/notes")
    NOTES_DIR: Path = PROJECT_ROOT / _raw_notes_dir if not Path(_raw_notes_dir).is_absolute() else Path(_raw_notes_dir)

    # Windows Applications Registry & Path Mappings
    LOCAL_APP_DATA = os.getenv("LOCALAPPDATA", "")
    PROGRAM_FILES = os.getenv("ProgramFiles", "C:\\Program Files")
    PROGRAM_FILES_X86 = os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)")

    APP_MAP: Dict[str, Dict[str, Any]] = {
        "whatsapp": {
            "name": "WhatsApp",
            "uri": "whatsapp:",
            "candidates": [
                Path(LOCAL_APP_DATA) / "WhatsApp" / "WhatsApp.exe",
                Path(LOCAL_APP_DATA) / "Programs" / "WhatsApp" / "WhatsApp.exe",
            ],
            "process": "WhatsApp.exe"
        },
        "chrome": {
            "name": "Google Chrome",
            "exe": "chrome.exe",
            "candidates": [
                Path(PROGRAM_FILES) / "Google" / "Chrome" / "Application" / "chrome.exe",
                Path(PROGRAM_FILES_X86) / "Google" / "Chrome" / "Application" / "chrome.exe",
                Path(LOCAL_APP_DATA) / "Google" / "Chrome" / "Application" / "chrome.exe",
            ],
            "process": "chrome.exe"
        },
        "vscode": {
            "name": "Visual Studio Code",
            "exe": "code",
            "candidates": [
                Path(LOCAL_APP_DATA) / "Programs" / "Microsoft VS Code" / "Code.exe",
                Path(PROGRAM_FILES) / "Microsoft VS Code" / "Code.exe",
                Path(PROGRAM_FILES_X86) / "Microsoft VS Code" / "Code.exe",
            ],
            "process": "Code.exe"
        },
        "notepad": {
            "name": "Notepad",
            "exe": "notepad.exe",
            "candidates": [Path("C:\\Windows\\System32\\notepad.exe")],
            "process": "notepad.exe"
        },
        "calculator": {
            "name": "Calculator",
            "exe": "calc.exe",
            "uri": "calculator:",
            "candidates": [Path("C:\\Windows\\System32\\calc.exe")],
            "process": "CalculatorApp.exe"
        },
        "explorer": {
            "name": "File Explorer",
            "exe": "explorer.exe",
            "candidates": [Path("C:\\Windows\\explorer.exe")],
            "process": "explorer.exe"
        },
        "taskmgr": {
            "name": "Task Manager",
            "exe": "taskmgr.exe",
            "candidates": [Path("C:\\Windows\\System32\\taskmgr.exe")],
            "process": "Taskmgr.exe"
        },
        "settings": {
            "name": "Windows Settings",
            "uri": "ms-settings:",
            "candidates": [],
            "process": "SystemSettings.exe"
        },
        "cmd": {
            "name": "Command Prompt",
            "exe": "cmd.exe",
            "candidates": [Path("C:\\Windows\\System32\\cmd.exe")],
            "process": "cmd.exe"
        },
        "powershell": {
            "name": "PowerShell",
            "exe": "powershell.exe",
            "candidates": [Path("C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe")],
            "process": "powershell.exe"
        },
        "paint": {
            "name": "Paint",
            "exe": "mspaint.exe",
            "candidates": [Path("C:\\Windows\\System32\\mspaint.exe")],
            "process": "mspaint.exe"
        },
        "edge": {
            "name": "Microsoft Edge",
            "exe": "msedge.exe",
            "candidates": [
                Path(PROGRAM_FILES_X86) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
                Path(PROGRAM_FILES) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            ],
            "process": "msedge.exe"
        },
        "spotify": {
            "name": "Spotify",
            "uri": "spotify:",
            "candidates": [
                Path(LOCAL_APP_DATA) / "Microsoft" / "WindowsApps" / "Spotify.exe",
                Path(LOCAL_APP_DATA) / "Spotify" / "Spotify.exe",
            ],
            "process": "Spotify.exe"
        }
    }

    # Common Web Sites Mappings
    WEBSITES: Dict[str, str] = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "stack overflow": "https://stackoverflow.com",
        "chatgpt": "https://chat.openai.com",
        "gmail": "https://mail.google.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "linkedin": "https://www.linkedin.com",
        "wikipedia": "https://www.wikipedia.org",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "netflix": "https://www.netflix.com",
    }


# Ensure directories exist
Config.NOTES_DIR.mkdir(parents=True, exist_ok=True)
