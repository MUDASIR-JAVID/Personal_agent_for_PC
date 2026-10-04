"""Speech Recognition Module for real-time microphone listening."""

from typing import Optional, List, Dict
import speech_recognition as sr
from src.config import Config
from src.utils.logger import logger, log_system, log_warning, log_error, log_user, console


class SpeechRecognizer:
    """Manages audio capture and transcription from microphone using SpeechRecognition."""

    def __init__(
        self,
        device_index: Optional[int] = None,
        energy_threshold: Optional[int] = None,
        pause_threshold: Optional[float] = None
    ) -> None:
        self.device_index = device_index if device_index is not None else Config.MICROPHONE_INDEX
        self.recognizer = sr.Recognizer()

        # Recognition parameters
        self.recognizer.energy_threshold = energy_threshold or Config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = pause_threshold or Config.PAUSE_THRESHOLD
        self.recognizer.non_speaking_duration = 0.5

        self._microphone: Optional[sr.Microphone] = None
        self._is_calibrated = False
        self._init_microphone()

    def _init_microphone(self) -> None:
        """Initialize the selected or default microphone device."""
        try:
            self._microphone = sr.Microphone(device_index=self.device_index)
        except Exception as e:
            logger.error(f"Failed to initialize microphone (index={self.device_index}): {e}")
            self._microphone = None

    @staticmethod
    def list_available_microphones() -> List[Dict[str, any]]:
        """List all available microphone input devices with their device indices."""
        try:
            names = sr.Microphone.list_microphone_names()
            return [{"index": i, "name": name} for i, name in enumerate(names)]
        except Exception as e:
            logger.error(f"Error enumerating microphones: {e}")
            return []

    def calibrate(self, duration: Optional[float] = None) -> bool:
        """Calibrate recognizer for ambient room noise."""
        if not self._microphone:
            self._init_microphone()
            if not self._microphone:
                log_error("Microphone not available for calibration.")
                return False

        dur = duration or Config.AMBIENT_ADJUST_DURATION
        log_system(f"Calibrating microphone for ambient noise ({dur:.1f}s)... Please remain quiet.")
        try:
            with self._microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=dur)
            self._is_calibrated = True
            log_system(f"Microphone calibrated. Energy threshold set to: {self.recognizer.energy_threshold:.1f}")
            return True
        except Exception as e:
            log_warning(f"Ambient noise calibration failed: {e}")
            return False

    def listen_once(
        self,
        timeout: Optional[float] = 5.0,
        phrase_time_limit: Optional[float] = None,
        prompt_message: Optional[str] = "Listening..."
    ) -> Optional[str]:
        """
        Listen for a single speech utterance and transcribe it to text.
        
        Returns:
            Transcribed text (lowercase, stripped), or None if silent / unrecognized.
        """
        if not self._microphone:
            self._init_microphone()
            if not self._microphone:
                log_error("Microphone is not available.")
                return None

        if not self._is_calibrated:
            self.calibrate()

        phrase_limit = phrase_time_limit or Config.PHRASE_TIME_LIMIT

        if prompt_message:
            console.print(f"[bold cyan]🎤 {prompt_message}[/bold cyan]", end="\r")

        try:
            with self._microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

            # Transcribe audio using Google Web Speech API
            text = self.recognizer.recognize_google(audio)
            if text:
                text = text.strip()
                log_user(text)
                return text

        except sr.WaitTimeoutError:
            # Normal timeout when user is not speaking
            return None

        except sr.UnknownValueError:
            # Speech detected but could not be understood
            log_warning("Speech was detected but could not be transcribed clearly.")
            return None

        except sr.RequestError as e:
            # Network failure or Google STT service drop
            log_error(f"Speech recognition service error (network/connectivity issue): {e}")
            return None

        except OSError as e:
            # Hardware disconnect, device busy, or audio driver issue
            log_error(f"Audio device error: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error during audio listening: {e}")
            return None

        return None

    def get_text_input(self, prompt: str = "Type command: ") -> Optional[str]:
        """Fallback console text input when microphone is disabled or unavailable."""
        try:
            raw = console.input(f"[bold green]💬 {prompt}[/bold green]")
            text = raw.strip()
            if text:
                log_user(text)
                return text
        except (KeyboardInterrupt, EOFError):
            return "exit"
        return None
