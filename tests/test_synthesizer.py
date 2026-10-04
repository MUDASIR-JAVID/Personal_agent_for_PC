"""Unit tests for text sanitization and speech synthesizer helper functions."""

import unittest
from src.speech.synthesizer import sanitize_for_speech


class TestSynthesizer(unittest.TestCase):
    """Test speech sanitization to ensure text-to-speech sounds natural."""

    def test_strip_markdown_bold_and_italics(self):
        raw = "This is **very important** and *italicized*."
        cleaned = sanitize_for_speech(raw)
        self.assertEqual(cleaned, "This is very important and italicized.")

    def test_strip_code_blocks(self):
        raw = "Here is the code: ```python\nprint('hello')\n``` That is it."
        cleaned = sanitize_for_speech(raw)
        self.assertIn("Code snippet omitted.", cleaned)
        self.assertNotIn("```", cleaned)

    def test_strip_urls(self):
        raw = "Visit https://google.com or http://example.org for info."
        cleaned = sanitize_for_speech(raw)
        self.assertNotIn("https://", cleaned)
        self.assertIn("link", cleaned)

    def test_strip_markdown_links(self):
        raw = "Check [Google Search](https://google.com) right now."
        cleaned = sanitize_for_speech(raw)
        self.assertEqual(cleaned, "Check Google Search right now.")

    def test_strip_bullets_and_hashes(self):
        raw = "# Header\n* Item 1\n* Item 2"
        cleaned = sanitize_for_speech(raw)
        self.assertNotIn("#", cleaned)
        self.assertNotIn("*", cleaned)
        self.assertIn("Header Item 1 Item 2", cleaned)


if __name__ == "__main__":
    unittest.main()
