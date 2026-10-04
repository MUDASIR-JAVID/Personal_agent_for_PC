"""Unit tests for system operations (time, date, notes, file ops)."""

import unittest
from pathlib import Path
from src.system.system_ops import SystemOps
from src.config import Config


class TestSystemOps(unittest.TestCase):
    """Test SystemOps functionality."""

    def test_get_current_time(self):
        time_msg = SystemOps.get_current_time()
        self.assertIn("The current time is", time_msg)
        self.assertTrue(time_msg.endswith("AM.") or time_msg.endswith("PM."))

    def test_get_current_date(self):
        date_msg = SystemOps.get_current_date()
        self.assertIn("Today is", date_msg)
        self.assertIn("202", date_msg)

    def test_take_and_read_notes(self):
        # Save a test note
        test_note = "Testing assistant automated unit test note"
        success, msg = SystemOps.take_note(test_note, custom_name="test_notes")
        self.assertTrue(success)
        self.assertIn(test_note, msg)

        # Read back notes
        read_success, read_msg = SystemOps.read_latest_notes(limit=1)
        self.assertTrue(read_success)
        self.assertIn(test_note, read_msg)

        # Clean up test file
        test_file = Config.NOTES_DIR / "test_notes.txt"
        if test_file.exists():
            test_file.unlink()

    def test_list_files(self):
        success, msg = SystemOps.list_files("notes")
        self.assertTrue(success)
        self.assertIn("Found", msg)


if __name__ == "__main__":
    unittest.main()
