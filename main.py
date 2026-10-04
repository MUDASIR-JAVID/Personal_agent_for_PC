#!/usr/bin/env python3
"""
Main Entry Point for the Desktop Voice-Controlled Assistant Agent.

Usage:
    python main.py                  # Start in real-time voice mode
    python main.py --text           # Start in interactive text mode
    python main.py --wake-word      # Require wake word (e.g. "Astra")
    python main.py --list-mics      # Enumerate microphone input devices
    python main.py --list-voices    # Enumerate installed TTS voices
    python main.py --test           # Run system self-test diagnostics
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.speech.recognizer import SpeechRecognizer
from src.speech.synthesizer import TextToSpeechSynthesizer
from src.core.assistant import VoiceAssistantAgent
from src.system.app_launcher import AppLauncher
from src.system.system_ops import SystemOps
from src.ai.gemini_client import GeminiClient
from src.utils.logger import console, print_banner


def list_microphones() -> None:
    """Print available audio input devices."""
    console.rule("[bold cyan]Available Audio Input Devices (Microphones)[/bold cyan]")
    mics = SpeechRecognizer.list_available_microphones()
    if not mics:
        console.print("[yellow]No microphone devices detected.[/yellow]")
        return

    for m in mics:
        console.print(f" [cyan]Index {m['index']:2d}:[/cyan] {m['name']}")
    console.print("\n[dim]To use a specific microphone, set MICROPHONE_INDEX in your .env file.[/dim]")


def list_voices() -> None:
    """Print available SAPI5 text-to-speech voices."""
    console.rule("[bold magenta]Available Text-to-Speech Voices[/bold magenta]")
    synthesizer = TextToSpeechSynthesizer()
    voices = synthesizer.list_available_voices()
    if not voices:
        console.print("[yellow]No text-to-speech voices found.[/yellow]")
        return

    for v in voices:
        console.print(f" [magenta]Index {v['index']}:[/magenta] {v['name']}")
        console.print(f"   [dim]ID: {v['id']}[/dim]")
    console.print("\n[dim]To select a voice, set VOICE_INDEX in your .env file.[/dim]")


def run_diagnostics() -> None:
    """Run an automated diagnostic test on assistant sub-modules."""
    console.rule("[bold green]Voice Assistant Diagnostics & Self-Test[/bold green]")

    # 1. Configuration check
    console.print("[bold]1. Checking Configuration:[/bold]")
    console.print(f"   - Assistant Name: [cyan]{Config.ASSISTANT_NAME}[/cyan]")
    console.print(f"   - Gemini Model:   [cyan]{Config.GEMINI_MODEL}[/cyan]")
    console.print(f"   - Gemini API Key: [cyan]{'Configured (hidden)' if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here' else 'Not configured (check .env)'}[/cyan]")
    console.print(f"   - Notes Dir:      [cyan]{Config.NOTES_DIR}[/cyan]")

    # 2. Text-to-Speech Test
    console.print("\n[bold]2. Testing Text-to-Speech (pyttsx3):[/bold]")
    try:
        tts = TextToSpeechSynthesizer()
        voices = tts.list_available_voices()
        console.print(f"   [green][+][/green] Found {len(voices)} installed voices.")
    except Exception as e:
        console.print(f"   [red][-][/red] TTS initialization failed: {e}")

    # 3. Speech Recognition Test
    console.print("\n[bold]3. Testing Speech Recognition & Microphone:[/bold]")
    try:
        mics = SpeechRecognizer.list_available_microphones()
        console.print(f"   [green][+][/green] Detected {len(mics)} audio input device channels.")
    except Exception as e:
        console.print(f"   [red][-][/red] Microphone enumeration failed: {e}")

    # 4. System Operations Test
    console.print("\n[bold]4. Testing System Operations (Time, Notes, Telemetry):[/bold]")
    time_str = SystemOps.get_current_time()
    console.print(f"   [green][+][/green] Time check: {time_str}")
    date_str = SystemOps.get_current_date()
    console.print(f"   [green][+][/green] Date check: {date_str}")
    _, status = SystemOps.get_system_status()
    console.print(f"   [green][+][/green] Telemetry: {status}")

    # 5. App Launcher Test
    console.print("\n[bold]5. Testing Application Mappings:[/bold]")
    apps = AppLauncher.list_supported_apps()
    console.print(f"   [green][+][/green] Loaded {len(apps)} predefined Windows app configurations.")
    notepad_exe = AppLauncher.find_executable("notepad")
    console.print(f"   [green][+][/green] Notepad path resolved to: {notepad_exe}")

    # 6. Gemini Client Test
    console.print("\n[bold]6. Testing Gemini AI Client:[/bold]")
    gemini = GeminiClient()
    if gemini.is_configured:
        console.print("   [green][+][/green] Gemini client is configured and ready.")
    else:
        console.print("   [yellow][!][/yellow] Gemini API key not set. Local system commands will still work!")

    console.rule("[bold green]Diagnostics Complete[/bold green]\n")


def main() -> None:
    """Parse command line arguments and execute assistant."""
    parser = argparse.ArgumentParser(
        description="Desktop Voice-Controlled Assistant Agent for Windows",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--text", "-t",
        action="store_true",
        help="Run in interactive text / console mode"
    )
    parser.add_argument(
        "--voice", "-v",
        action="store_true",
        help="Run in real-time voice mode (default)"
    )
    parser.add_argument(
        "--wake-word", "-w",
        action="store_true",
        help="Require wake word (e.g. 'Astra') before executing commands"
    )
    parser.add_argument(
        "--list-mics",
        action="store_true",
        help="List available microphone devices and exit"
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available TTS voices and exit"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run diagnostic self-tests and exit"
    )

    args = parser.parse_args()

    # Utility flags
    if args.list_mics:
        list_microphones()
        return

    if args.list_voices:
        list_voices()
        return

    if args.test:
        run_diagnostics()
        return

    # Determine execution mode (default to voice unless text flag is explicitly passed)
    mode = "text" if args.text else "voice"

    # Launch assistant
    assistant = VoiceAssistantAgent(
        mode=mode,
        require_wake_word=args.wake_word
    )
    assistant.start()


if __name__ == "__main__":
    main()
