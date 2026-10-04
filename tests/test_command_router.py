"""Unit tests for the CommandRouter logic."""

import unittest
from unittest.mock import MagicMock
from src.core.command_router import CommandRouter
from src.ai.gemini_client import GeminiClient


class TestCommandRouter(unittest.TestCase):
    """Test command parsing and intent routing."""

    def setUp(self):
        # Mock GeminiClient to test routing without network calls
        self.mock_gemini = MagicMock(spec=GeminiClient)
        self.mock_gemini.ask.return_value = "This is a simulated Gemini answer."
        self.router = CommandRouter(gemini_client=self.mock_gemini)

    def test_exit_command(self):
        for phrase in ["exit", "quit", "goodbye", "stop"]:
            handled, msg, should_exit = self.router.process(phrase)
            self.assertTrue(handled)
            self.assertTrue(should_exit)
            self.assertIn("Goodbye", msg)

    def test_time_command(self):
        handled, msg, should_exit = self.router.process("what time is it")
        self.assertTrue(handled)
        self.assertFalse(should_exit)
        self.assertIn("The current time is", msg)

    def test_date_command(self):
        handled, msg, should_exit = self.router.process("what date is it")
        self.assertTrue(handled)
        self.assertFalse(should_exit)
        self.assertIn("Today is", msg)

    def test_note_command(self):
        handled, msg, should_exit = self.router.process("take a note buy groceries at 6pm")
        self.assertTrue(handled)
        self.assertFalse(should_exit)
        self.assertIn("buy groceries at 6pm", msg)

    def test_help_command(self):
        handled, msg, should_exit = self.router.process("what can you do")
        self.assertTrue(handled)
        self.assertFalse(should_exit)
        self.assertIn("I can open applications", msg)

    def test_gemini_fallback(self):
        # Unrecognized command routes to Gemini
        handled, msg, should_exit = self.router.process("explain how black holes form")
        self.assertTrue(handled)
        self.assertFalse(should_exit)
        self.assertEqual(msg, "This is a simulated Gemini answer.")
        self.mock_gemini.ask.assert_called_once_with("explain how black holes form")


if __name__ == "__main__":
    unittest.main()
