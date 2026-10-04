"""Web Controller for launching websites and executing web searches."""

import webbrowser
import urllib.parse
from typing import Tuple
from src.config import Config
from src.utils.logger import logger, log_system, log_error


class WebController:
    """Manages browser interactions, website navigation, and web search engines."""

    @classmethod
    def open_url(cls, url: str) -> Tuple[bool, str]:
        """Open any URL in the user's default web browser."""
        if not url:
            return False, "No URL provided."

        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        try:
            log_system(f"Opening URL: {url}")
            webbrowser.open(url, new=2)
            return True, f"Opening {url}"
        except Exception as e:
            log_error(f"Failed to open URL '{url}': {e}")
            return False, f"Could not open website: {e}"

    @classmethod
    def open_website(cls, site_name: str) -> Tuple[bool, str]:
        """Open a recognized website or fall back to .com domain."""
        clean = site_name.strip().lower()
        # Direct lookup in pre-configured websites
        if clean in Config.WEBSITES:
            url = Config.WEBSITES[clean]
            cls.open_url(url)
            return True, f"Opening {clean.capitalize()}."

        # Domain pattern check (e.g., example.org, github.io)
        if "." in clean:
            url = f"https://{clean}"
            cls.open_url(url)
            return True, f"Opening {clean}."

        # Default fallback: .com domain
        url = f"https://www.{clean}.com"
        cls.open_url(url)
        return True, f"Opening {clean.capitalize()}."

    @classmethod
    def search_google(cls, query: str) -> Tuple[bool, str]:
        """Perform a Google search query."""
        if not query.strip():
            return False, "Search query was empty."

        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.google.com/search?q={encoded}"
        log_system(f"Searching Google for: '{query}'")
        cls.open_url(url)
        return True, f"Searching Google for {query}."

    @classmethod
    def search_youtube(cls, query: str) -> Tuple[bool, str]:
        """Search YouTube for videos or music."""
        if not query.strip():
            return False, "Search query was empty."

        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        log_system(f"Searching YouTube for: '{query}'")
        cls.open_url(url)
        return True, f"Searching YouTube for {query}."

    @classmethod
    def search_github(cls, query: str) -> Tuple[bool, str]:
        """Search repositories on GitHub."""
        if not query.strip():
            return False, "Search query was empty."

        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://github.com/search?q={encoded}"
        log_system(f"Searching GitHub for: '{query}'")
        cls.open_url(url)
        return True, f"Searching GitHub for {query}."

    @classmethod
    def search_wikipedia(cls, query: str) -> Tuple[bool, str]:
        """Search Wikipedia."""
        if not query.strip():
            return False, "Search query was empty."

        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}"
        log_system(f"Searching Wikipedia for: '{query}'")
        cls.open_url(url)
        return True, f"Searching Wikipedia for {query}."
