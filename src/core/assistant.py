"""Main Voice Assistant Orchestrator Agent."""

import time
from typing import Optional
from src.config import Config
from src.speech.recognizer import SpeechRecognizer
from src.speech.synthesizer import TextToSpeechSynthesizer
from src.ai.gemini_client import GeminiClient
from src.core.command_router import CommandRouter
from src.utils.logger import (
    logger,
    print_banner,
    log_info,
    log_warning,
    log_error,
    console
)


class VoiceAssistantAgent:
    """Production-ready desktop voice-controlled assistant."""

    def __init__(
        self,
        mode: str = "voice",
        require_wake_word: bool = False
    ) -> None:
        self.mode = mode.lower()
        self.require_wake_word = require_wake_word
        self.is_running = False

        # Initialize components
        self.synthesizer = TextToSpeechSynthesizer()
        self.recognizer = SpeechRecognizer()
        self.gemini = GeminiClient()
        self.router = CommandRouter(gemini_client=self.gemini)

    def speak(self, text: str) -> None:
        """Speak out text and log to console."""
        self.synthesizer.speak(text)

    def execute_command(self, query: str) -> bool:
        """
        Process a single query.
        
        Returns:
            should_exit (bool): True if exit requested.
        """
        if not query or not query.strip():
            return False

        try:
            handled, response, should_exit = self.router.process(query)
            if response:
                self.speak(response)
            return should_exit
        except Exception as e:
            log_error(f"Error executing command '{query}': {e}")
            self.speak("Sorry, I encountered an error while processing that command.")
            return False

    def is_wake_word_triggered(self, text: str) -> bool:
        """Check if user query contains any configured wake words."""
        if not self.require_wake_word or not Config.WAKE_WORDS:
            return True

        lower = text.lower()
        return any(wake in lower for wake in Config.WAKE_WORDS)

    def start(self) -> None:
        """Start the assistant's main listening and response loop."""
        print_banner(assistant_name=Config.ASSISTANT_NAME, mode=self.mode)

        # Startup greeting
        startup_msg = f"Hello! I am {Config.ASSISTANT_NAME}. How can I help you today?"
        self.speak(startup_msg)

        if self.mode == "voice":
            # Calibrate microphone
            self.recognizer.calibrate()
            console.print("[dim]Tip: Say 'exit' or press Ctrl+C anytime to stop.[/dim]\n")
        else:
            console.print("[dim]Tip: Type 'exit' or press Ctrl+C anytime to stop.[/dim]\n")

        self.is_running = True

        try:
            while self.is_running:
                query: Optional[str] = None

                if self.mode == "voice":
                    query = self.recognizer.listen_once(
                        timeout=5.0,
                        phrase_time_limit=Config.PHRASE_TIME_LIMIT,
                        prompt_message="Listening for your command..."
                    )
                else:
                    query = self.recognizer.get_text_input(prompt=f"{Config.ASSISTANT_NAME} > ")

                if not query:
                    # Silence or timeout, continue listening
                    time.sleep(0.1)
                    continue

                # Check wake word if required
                if self.require_wake_word and not self.is_wake_word_triggered(query):
                    logger.debug(f"Ignored non-wake phrase: '{query}'")
                    continue

                should_exit = self.execute_command(query)
                if should_exit:
                    self.is_running = False
                    break

        except KeyboardInterrupt:
            console.print("\n[yellow]Keyboard interrupt detected.[/yellow]")
            self.speak(f"Goodbye! Shutting down {Config.ASSISTANT_NAME}.")
        except Exception as e:
            log_error(f"Critical loop exception: {e}")
            self.speak("An unexpected error occurred. Assistant is safely shutting down.")
        finally:
            self.is_running = False
            self.synthesizer.stop()
            console.print("[dim]Assistant session terminated.[/dim]")
