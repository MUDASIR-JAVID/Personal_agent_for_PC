"""Google Gemini AI Integration for intelligent voice and conversation handling."""

from typing import Optional, List
from google import genai
from google.genai import types
from google.genai.errors import APIError
from src.config import Config
from src.utils.logger import logger, log_warning, log_error, log_info


class GeminiClient:
    """Manages conversational reasoning, question answering, and intent understanding via Gemini."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        assistant_name: Optional[str] = None
    ) -> None:
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = model_name or Config.GEMINI_MODEL
        self.assistant_name = assistant_name or Config.ASSISTANT_NAME

        self._client: Optional[genai.Client] = None
        self._chat = None
        self._is_ready = False

        self._init_client()

    @property
    def is_configured(self) -> bool:
        """Check if Gemini API is configured with a valid key."""
        return self._is_ready and self._client is not None

    def _init_client(self) -> None:
        """Initialize the Gemini client and chat session."""
        if not self.api_key or self.api_key.strip() in ("", "your_gemini_api_key_here"):
            logger.info("Gemini API key is not configured. AI fallback responses will be simulated or prompt user.")
            self._is_ready = False
            return

        try:
            self._client = genai.Client(api_key=self.api_key)
            self._system_instruction = (
                f"You are {self.assistant_name}, a friendly, intelligent, and highly capable desktop voice assistant "
                f"running locally on the user's Windows computer.\n"
                f"Guidelines for your responses:\n"
                f"1. Your answers will be spoken aloud to the user via Text-to-Speech.\n"
                f"2. Keep answers concise, clear, and natural (1 to 3 sentences maximum), unless the user explicitly requests an in-depth explanation.\n"
                f"3. Never include markdown symbols like asterisks, bullet points, headers (#), or code fences, because they sound awkward when read aloud.\n"
                f"4. If asked to perform local desktop actions (e.g. open apps, notes), acknowledge politely."
            )

            self.reset_chat()
            self._is_ready = True
            logger.info(f"Gemini AI initialized successfully with model: {self.model_name}")
        except Exception as e:
            log_error(f"Failed to initialize Gemini AI client: {e}")
            self._is_ready = False

    def reset_chat(self) -> None:
        """Reset multi-turn chat session history."""
        if not self._client:
            return

        try:
            config = types.GenerateContentConfig(
                system_instruction=self._system_instruction,
                temperature=0.7,
                max_output_tokens=300,
            )
            self._chat = self._client.chats.create(
                model=self.model_name,
                config=config
            )
        except Exception as e:
            logger.warning(f"Failed to create chat session: {e}")
            self._chat = None

    def ask(self, prompt: str) -> str:
        """
        Send a user query to Gemini and receive a spoken-friendly answer.
        
        Args:
            prompt: User utterance or general question.
            
        Returns:
            Concise, conversational text response.
        """
        if not prompt or not prompt.strip():
            return "I did not catch that. Could you repeat?"

        if not self.is_configured:
            return (
                "Gemini AI is not configured. Please add your GEMINI_API_KEY to the dot-env file "
                "to enable general knowledge and smart reasoning."
            )

        try:
            # Use multi-turn chat if available
            if self._chat:
                response = self._chat.send_message(prompt)
                if response and response.text:
                    return response.text.strip()

            # Fallback to direct model generation
            config = types.GenerateContentConfig(
                system_instruction=self._system_instruction,
                temperature=0.7,
                max_output_tokens=300,
            )
            res = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            if res and res.text:
                return res.text.strip()

            return "I processed your request, but did not receive any text response."

        except APIError as e:
            log_error(f"Gemini API error ({e.code}): {e.message}")
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                return "My Gemini AI quota has been reached. Please check your API quota in Google AI Studio."
            elif "key" in str(e).lower() or "auth" in str(e).lower():
                return "There seems to be an issue with your Gemini API key. Please check your credentials."
            return "I encountered an error communicating with Gemini AI. Please check your network connection."

        except Exception as e:
            log_error(f"Unexpected error while querying Gemini: {e}")
            return "Sorry, I ran into a technical issue while processing your question."
