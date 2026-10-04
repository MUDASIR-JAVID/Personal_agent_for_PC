"""Command Router: parses voice/text inputs and routes them to appropriate handlers."""

import re
from typing import Tuple, Optional
from src.config import Config
from src.system.app_launcher import AppLauncher
from src.system.web_controller import WebController
from src.system.system_ops import SystemOps
from src.ai.gemini_client import GeminiClient
from src.utils.logger import logger, log_info


class CommandRouter:
    """Classifies user queries and executes local system tasks or queries Gemini AI."""

    def __init__(self, gemini_client: Optional[GeminiClient] = None) -> None:
        self.gemini = gemini_client or GeminiClient()

    def process(self, query: str) -> Tuple[bool, str, bool]:
        """
        Process a user command or query.
        
        Args:
            query: The user input text.
            
        Returns:
            Tuple of:
            - is_handled (bool): True if command was executed or responded to.
            - response_text (str): Spoken-friendly response for user.
            - should_exit (bool): True if user requested assistant shutdown.
        """
        if not query or not query.strip():
            return False, "", False

        text = query.strip()
        lower = text.lower()

        # Remove assistant name or wake word prefixes if user said "Astra, what time is it?"
        for wake in Config.WAKE_WORDS:
            if lower.startswith(wake):
                lower = lower[len(wake):].lstrip(",.:;! ").strip()
                # Also trim original text
                text = text[len(wake):].lstrip(",.:;! ").strip()
                break

        # 1. Exit / Shutdown commands
        exit_patterns = [
            r"^(exit|quit|bye|goodbye|stop|shutdown|close assistant|stop listening)$",
            r"^(shut down|see you later|power off)$"
        ]
        if any(re.match(p, lower) for p in exit_patterns):
            return True, f"Goodbye! Have a great day.", True

        # 2. Help / Identity commands
        if lower in ("help", "what can you do", "features", "commands", "who are you"):
            help_text = (
                f"I am {Config.ASSISTANT_NAME}, your personal desktop voice assistant. "
                "I can open applications like WhatsApp, Chrome, or VS Code, "
                "search the web, tell the time and date, take notes, check system battery and files, "
                "or answer any general question using Google Gemini AI."
            )
            return True, help_text, False

        # 3. Time & Date
        if any(p in lower for p in ["what time is it", "tell me the time", "current time", "what is the time"]):
            return True, SystemOps.get_current_time(), False

        if any(p in lower for p in ["what date is it", "today's date", "what is the date", "what day is it", "tell me the date"]):
            return True, SystemOps.get_current_date(), False

        # 4. System Status & Battery
        if any(p in lower for p in ["system status", "battery status", "battery level", "how much battery", "cpu usage", "ram usage"]):
            _, report = SystemOps.get_system_status()
            return True, report, False

        # 5. Note Taking & Reading
        # Match "take a note <text>", "note that <text>", "write note <text>", "write a note <text>"
        note_match = re.search(r"^(?:take a note|take note|write a note|write note|save note|note that)\s+(.*)$", lower)
        if note_match:
            note_content = note_match.group(1).strip()
            _, msg = SystemOps.take_note(note_content)
            return True, msg, False

        if any(p in lower for p in ["read my notes", "read notes", "show my notes", "what are my notes", "latest notes"]):
            _, msg = SystemOps.read_latest_notes()
            return True, msg, False

        # 6. File & Folder Operations
        # "list files in downloads", "show files in documents"
        list_match = re.search(r"^(?:list files in|show files in|list files|what files are in)\s*(.*)$", lower)
        if list_match:
            folder = list_match.group(1).strip() or "documents"
            _, msg = SystemOps.list_files(folder)
            return True, msg, False

        # "open folder downloads", "open downloads folder"
        folder_match = re.search(r"^open\s+(downloads|documents|desktop|notes|project)\s+folder$", lower)
        if folder_match:
            folder = folder_match.group(1).strip()
            _, msg = SystemOps.open_folder(folder)
            return True, msg, False

        # 7. Web Searching & Navigation
        # Specific search engines
        yt_search = re.search(r"^(?:search youtube for|play on youtube|youtube search)\s+(.*)$", lower)
        if yt_search:
            q = yt_search.group(1).strip()
            _, msg = WebController.search_youtube(q)
            return True, msg, False

        gh_search = re.search(r"^(?:search github for|github search)\s+(.*)$", lower)
        if gh_search:
            q = gh_search.group(1).strip()
            _, msg = WebController.search_github(q)
            return True, msg, False

        wiki_search = re.search(r"^(?:search wikipedia for|wikipedia search)\s+(.*)$", lower)
        if wiki_search:
            q = wiki_search.group(1).strip()
            _, msg = WebController.search_wikipedia(q)
            return True, msg, False

        google_search = re.search(r"^(?:search google for|google|search for|search the web for)\s+(.*)$", lower)
        if google_search:
            q = google_search.group(1).strip()
            _, msg = WebController.search_google(q)
            return True, msg, False

        # Opening specific website ("open youtube", "open github", "open reddit", "open website <url>")
        web_open_match = re.search(r"^(?:open website|open site)\s+(.*)$", lower)
        if web_open_match:
            target = web_open_match.group(1).strip()
            _, msg = WebController.open_website(target)
            return True, msg, False

        for site_key in Config.WEBSITES:
            if lower == f"open {site_key}":
                _, msg = WebController.open_website(site_key)
                return True, msg, False

        # 8. Application Launching & Closing
        # "close chrome", "close notepad", "terminate whatsapp"
        close_match = re.search(r"^(?:close|terminate|kill|exit)\s+(.*)$", lower)
        if close_match:
            app_target = close_match.group(1).strip()
            # Verify if this is an app name
            if app_target in Config.APP_MAP or any(app_target in alias for alias in Config.APP_MAP):
                _, msg = AppLauncher.close_app(app_target)
                return True, msg, False

        # "open chrome", "launch whatsapp", "start vs code", "open notepad"
        open_app_match = re.search(r"^(?:open|launch|start|run)\s+(.*)$", lower)
        if open_app_match:
            app_target = open_app_match.group(1).strip()
            # If target is a known app or app-like command
            if app_target in Config.APP_MAP or app_target in ["whatsapp", "chrome", "vscode", "vs code", "notepad", "calculator", "explorer", "settings"]:
                _, msg = AppLauncher.open_app(app_target)
                return True, msg, False
            elif AppLauncher.find_executable(app_target):
                _, msg = AppLauncher.open_app(app_target)
                return True, msg, False

        # 9. Fallback: Gemini AI Knowledge & Intent Handling
        # General questions, complex reasoning, or open conversation
        log_info(f"Querying Gemini AI for: '{text}'")
        ai_response = self.gemini.ask(text)
        return True, ai_response, False
