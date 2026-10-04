"""Basic system operations: time, date, notes, file management, and hardware status."""

import os
import datetime
from pathlib import Path
from typing import Tuple, Optional, List
import psutil
from src.config import Config
from src.utils.logger import logger, log_system, log_error, log_info


class SystemOps:
    """Manages local system tasks, file operations, note taking, and hardware telemetry."""

    @classmethod
    def get_current_time(cls) -> str:
        """Get the current time in spoken-friendly format."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        # Strip leading zero if present on hour (e.g., 09:15 PM -> 9:15 PM)
        if time_str.startswith("0"):
            time_str = time_str[1:]
        return f"The current time is {time_str}."

    @classmethod
    def get_current_date(cls) -> str:
        """Get the current date in spoken-friendly format."""
        now = datetime.datetime.now()
        day = now.day
        # Add ordinal suffix to day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        date_str = now.strftime(f"%A, %B {day}{suffix}, %Y")
        return f"Today is {date_str}."

    @classmethod
    def take_note(cls, note_text: str, custom_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save a voice note to the local notes storage with timestamp.
        """
        if not note_text or not note_text.strip():
            return False, "Cannot save an empty note."

        clean_text = note_text.strip()
        now = datetime.datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%I:%M:%S %p")

        notes_dir = Config.NOTES_DIR
        notes_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{custom_name}.txt" if custom_name else f"notes_{today_date}.txt"
        file_path = notes_dir / filename

        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {clean_text}\n")

            log_system(f"Saved note to {file_path}: '{clean_text}'")
            return True, f"I have saved that note for you: '{clean_text}'."
        except Exception as e:
            log_error(f"Failed to save note: {e}")
            return False, f"Sorry, I failed to write your note to disk: {e}"

    @classmethod
    def read_latest_notes(cls, limit: int = 3) -> Tuple[bool, str]:
        """
        Read the most recently added notes.
        """
        notes_dir = Config.NOTES_DIR
        if not notes_dir.exists():
            return True, "You do not have any notes saved yet."

        note_files = sorted(notes_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)
        if not note_files:
            return True, "You do not have any notes recorded."

        latest_file = note_files[0]
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                return True, "Your current note file is empty."

            recent = lines[-limit:]
            summary = " Here are your latest notes: " + " Next note: ".join(recent)
            return True, summary
        except Exception as e:
            log_error(f"Error reading notes: {e}")
            return False, f"Could not read your notes: {e}"

    @classmethod
    def list_files(cls, target_folder: Optional[str] = None) -> Tuple[bool, str]:
        """
        List files in common user directories (documents, downloads, desktop, or current dir).
        """
        user_profile = Path(os.environ.get("USERPROFILE", "C:\\Users\\Default"))
        folder_aliases = {
            "downloads": user_profile / "Downloads",
            "download": user_profile / "Downloads",
            "documents": user_profile / "Documents",
            "document": user_profile / "Documents",
            "desktop": user_profile / "Desktop",
            "notes": Config.NOTES_DIR,
            "project": Config.ROOT_DIR,
            "here": Config.ROOT_DIR,
        }

        key = (target_folder or "documents").strip().lower()
        target_path = folder_aliases.get(key, user_profile / target_folder if target_folder else user_profile / "Documents")

        if not target_path.exists() or not target_path.is_dir():
            return False, f"The folder '{target_folder}' does not exist on your computer."

        try:
            items = [item.name for item in target_path.iterdir() if not item.name.startswith(".")]
            if not items:
                return True, f"The {key} folder is empty."

            top_items = items[:5]
            display = ", ".join(top_items)
            msg = f"Found {len(items)} items in {key}. The top files are: {display}."
            log_system(msg)
            return True, msg
        except Exception as e:
            log_error(f"Failed to list directory contents: {e}")
            return False, f"Could not access {target_folder}: {e}"

    @classmethod
    def open_folder(cls, target_folder: Optional[str] = None) -> Tuple[bool, str]:
        """Open a directory in Windows Explorer."""
        user_profile = Path(os.environ.get("USERPROFILE", "C:\\Users\\Default"))
        folder_aliases = {
            "downloads": user_profile / "Downloads",
            "documents": user_profile / "Documents",
            "desktop": user_profile / "Desktop",
            "notes": Config.NOTES_DIR,
            "project": Config.ROOT_DIR,
        }
        key = (target_folder or "documents").strip().lower()
        target_path = folder_aliases.get(key, user_profile / target_folder if target_folder else user_profile / "Documents")

        if not target_path.exists():
            return False, f"Folder {target_folder} does not exist."

        try:
            os.startfile(str(target_path))
            return True, f"Opening {key} folder in File Explorer."
        except Exception as e:
            log_error(f"Failed to open folder: {e}")
            return False, f"Could not open folder: {e}"

    @classmethod
    def get_system_status(cls) -> Tuple[bool, str]:
        """
        Check battery status, CPU load, and RAM usage.
        """
        parts = []

        # Battery Status
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                percent = int(battery.percent)
                plugged = "plugged in" if battery.power_plugged else "on battery power"
                parts.append(f"Battery is at {percent} percent and {plugged}.")
        except Exception as e:
            logger.debug(f"Battery info not available: {e}")

        # CPU & Memory
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            parts.append(f"CPU usage is at {cpu_usage:.0f} percent. Memory usage is at {memory.percent:.0f} percent.")
        except Exception as e:
            logger.debug(f"Hardware stats unavailable: {e}")

        if not parts:
            return False, "Could not retrieve system telemetry."

        report = " ".join(parts)
        log_system(report)
        return True, report
