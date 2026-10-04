"""Unit tests for application launcher resolution."""

import unittest
from src.system.app_launcher import AppLauncher


class TestAppLauncher(unittest.TestCase):
    """Test AppLauncher path resolution and listings."""

    def test_list_supported_apps(self):
        apps = AppLauncher.list_supported_apps()
        self.assertIn("whatsapp", apps)
        self.assertIn("chrome", apps)
        self.assertIn("vscode", apps)
        self.assertIn("notepad", apps)
        self.assertIn("calculator", apps)

    def test_find_notepad_executable(self):
        exe = AppLauncher.find_executable("notepad")
        self.assertIsNotNone(exe)
        self.assertTrue(exe.lower().endswith("notepad.exe"))

    def test_unknown_app_graceful_handling(self):
        success, msg = AppLauncher.open_app("non_existent_fake_app_xyz")
        self.assertFalse(success)
        self.assertIn("could not find", msg.lower())


if __name__ == "__main__":
    unittest.main()
