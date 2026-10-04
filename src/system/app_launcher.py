"""System Control & Application Launcher for Windows."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from src.config import Config
from src.utils.logger import logger, log_system, log_error, log_warning


class AppLauncher:
    """Manages secure application launching and process control on Windows."""

    @classmethod
    def find_executable(cls, app_key: str) -> Optional[str]:
        """
        Locate the executable path for a given application key or name.
        Checks:
        1. Config candidate paths
        2. System PATH (via shutil.which)
        3. Standard Windows system directories
        """
        app_info = Config.APP_MAP.get(app_key.lower())
        if app_info:
            # Check explicit candidates
            for candidate in app_info.get("candidates", []):
                p = Path(candidate)
                if p.exists() and p.is_file():
                    return str(p)

            # Check if defined exe is in system PATH
            exe_name = app_info.get("exe")
            if exe_name:
                found = shutil.which(exe_name)
                if found:
                    return found

        # If not found in APP_MAP, try generic which
        direct_which = shutil.which(app_key)
        if direct_which:
            return direct_which

        return None

    @classmethod
    def open_app(cls, app_name: str) -> Tuple[bool, str]:
        """
        Launch an application securely by name or alias.
        
        Args:
            app_name: The application name requested by the user.
            
        Returns:
            Tuple of (success_bool, message_string)
        """
        clean_name = app_name.strip().lower()

        # Handle aliases and common variations
        name_aliases = {
            "google chrome": "chrome",
            "browser": "chrome",
            "visual studio code": "vscode",
            "vs code": "vscode",
            "code editor": "vscode",
            "whats app": "whatsapp",
            "text editor": "notepad",
            "note pad": "notepad",
            "calc": "calculator",
            "math": "calculator",
            "files": "explorer",
            "my computer": "explorer",
            "folder": "explorer",
            "task manager": "taskmgr",
            "terminal": "powershell",
            "command prompt": "cmd",
            "mspaint": "paint",
            "drawing": "paint",
            "microsoft edge": "edge",
        }
        target_key = name_aliases.get(clean_name, clean_name)
        app_config = Config.APP_MAP.get(target_key)
        display_name = app_config.get("name", app_name.title()) if app_config else app_name.title()

        # 1. Try Windows URI scheme if configured (e.g. whatsapp:, ms-settings:, calculator:)
        if app_config and "uri" in app_config:
            uri = app_config["uri"]
            try:
                log_system(f"Launching {display_name} via protocol URI '{uri}'...")
                os.startfile(uri)
                return True, f"Opening {display_name}."
            except Exception as e:
                logger.debug(f"Protocol launch failed for {uri}: {e}. Falling back to executable scan...")

        # 2. Try locating executable
        exe_path = cls.find_executable(target_key)
        if exe_path:
            try:
                log_system(f"Starting {display_name} from: {exe_path}")
                # Safe launch without shell=True to prevent injection
                subprocess.Popen([exe_path], close_fds=True)
                return True, f"Opening {display_name}."
            except Exception as e:
                log_error(f"Failed to launch executable {exe_path}: {e}")
                return False, f"Could not open {display_name}: {e}"

        # 3. Fallback: try Windows os.startfile for Windows Store or registered system app
        try:
            target_str = app_config.get("exe", target_key) if app_config else target_key
            log_system(f"Attempting system startfile for '{target_str}'...")
            os.startfile(target_str)
            return True, f"Opening {display_name}."
        except Exception as e:
            logger.warning(f"System startfile failed for '{target_key}': {e}")

        return False, f"Sorry, I could not find or launch {app_name} on your laptop."

    @classmethod
    def close_app(cls, app_name: str) -> Tuple[bool, str]:
        """
        Close a running application process on Windows.
        
        Args:
            app_name: The application name or alias to terminate.
            
        Returns:
            Tuple of (success_bool, message_string)
        """
        clean_name = app_name.strip().lower()
        name_aliases = {
            "google chrome": "chrome",
            "visual studio code": "vscode",
            "vs code": "vscode",
            "whats app": "whatsapp",
            "calculator": "calc",
            "task manager": "taskmgr",
        }
        target_key = name_aliases.get(clean_name, clean_name)
        app_config = Config.APP_MAP.get(target_key)
        process_name = app_config.get("process") if app_config else f"{target_key}.exe"
        display_name = app_config.get("name", app_name.title()) if app_config else app_name.title()

        try:
            # Use taskkill securely with strict arguments
            result = subprocess.run(
                ["taskkill", "/F", "/IM", process_name],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                log_system(f"Terminated process: {process_name}")
                return True, f"Closed {display_name}."
            else:
                return False, f"{display_name} was not running."
        except Exception as e:
            log_error(f"Error terminating {process_name}: {e}")
            return False, f"Failed to close {display_name}."

    @classmethod
    def list_supported_apps(cls) -> Dict[str, str]:
        """Get a dictionary of pre-mapped applications."""
        return {k: v.get("name", k) for k, v in Config.APP_MAP.items()}
