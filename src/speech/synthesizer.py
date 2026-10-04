"""Text-to-Speech (TTS) Synthesizer Module."""

import re
import threading
from typing import Optional
import pyttsx3
from src.config import Config
from src.utils.logger import logger, log_assistant, log_error, log_warning


def sanitize_for_speech(text: str) -> str:
    """Sanitize text to remove markdown, URLs, and code blocks for fluid speech synthesis."""
    if not text:
        return ""

    # Remove code blocks ```...```
    text = re.sub(r"```[\s\S]*?```", " Code snippet omitted. ", text)
    # Remove inline code `...`
    text = re.sub(r"`[^`]*`", "", text)
    # Remove markdown links [title](url) -> title
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove raw URLs
    text = re.sub(r"https?://\S+|www\.\S+", " link ", text)
    # Remove markdown headers and formatting (*, _, #, ~, >)
    text = re.sub(r"[\*\_#~>]", "", text)
    # Normalize bullet points and dashes
    text = re.sub(r"^\s*[-•*]\s*", "", text, flags=re.MULTILINE)
    # Collapse multiple whitespaces and newlines
    text = re.sub(r"\s+", " ", text).strip()

    return text


class TextToSpeechSynthesizer:
    """Manages audio text-to-speech synthesis using pyttsx3 (SAPI5)."""

    def __init__(
        self,
        rate: Optional[int] = None,
        volume: Optional[float] = None,
        voice_index: Optional[int] = None
    ) -> None:
        self.rate = rate or Config.SPEECH_RATE
        self.volume = volume or Config.SPEECH_VOLUME
        self.voice_index = voice_index if voice_index is not None else Config.VOICE_INDEX
        self._lock = threading.Lock()
        self._engine = None
        self._init_engine()

    def _init_engine(self) -> None:
        """Initialize the pyttsx3 engine safely."""
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)

            voices = self._engine.getProperty("voices")
            if voices and self.voice_index is not None:
                if 0 <= self.voice_index < len(voices):
                    self._engine.setProperty("voice", voices[self.voice_index].id)
                    logger.debug(f"Selected voice: {voices[self.voice_index].name}")
                else:
                    self._engine.setProperty("voice", voices[0].id)
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 engine: {e}")
            self._engine = None

    def list_available_voices(self) -> list:
        """Return a list of installed voices with details."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            result = []
            for idx, v in enumerate(voices):
                result.append({
                    "index": idx,
                    "id": v.id,
                    "name": v.name,
                    "languages": getattr(v, "languages", []),
                    "gender": getattr(v, "gender", "unknown")
                })
            engine.stop()
            return result
        except Exception as e:
            logger.warning(f"Could not retrieve voice list: {e}")
            return []

    def speak(self, text: str, print_to_console: bool = True) -> None:
        """Convert text to speech and play it through speakers safely."""
        if not text or not text.strip():
            return

        if print_to_console:
            log_assistant(text)

        cleaned_text = sanitize_for_speech(text)
        if not cleaned_text:
            return

        with self._lock:
            try:
                # Re-verify engine is initialized
                if self._engine is None:
                    self._init_engine()

                if self._engine:
                    self._engine.say(cleaned_text)
                    self._engine.runAndWait()
            except RuntimeError as e:
                # Loop already started or engine busy
                logger.warning(f"TTS runtime notice: {e}, re-initializing engine...")
                self._init_engine()
                try:
                    if self._engine:
                        self._engine.say(cleaned_text)
                        self._engine.runAndWait()
                except Exception as inner_e:
                    logger.error(f"TTS retry failed: {inner_e}")
            except Exception as e:
                log_error(f"Text-to-speech failed: {e}")

    def stop(self) -> None:
        """Stop current speech synthesis."""
        with self._lock:
            if self._engine:
                try:
                    self._engine.stop()
                except Exception as e:
                    logger.debug(f"Error stopping engine: {e}")
