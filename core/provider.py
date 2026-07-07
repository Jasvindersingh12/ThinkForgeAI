import json
import os
from pathlib import Path

from core.gemini import Gemini


class Provider:

    def __init__(self):
        self.gemini = Gemini()
        self.mock_folder = Path("mock")

    @property
    def force_mock(self) -> bool:
        """Controlled by the sidebar's Mock Mode toggle via env var."""
        return os.environ.get("THINKFORGE_MOCK", "0") == "1"

    def _load_mock(self, mock_file):
        with open(self.mock_folder / mock_file, encoding="utf8") as f:
            return json.load(f)

    def ask_json(self, prompt, mock_file):

        if self.force_mock:
            print()
            print("=" * 60)
            print("Mock Mode ON (THINKFORGE_MOCK=1) — skipping Gemini call")
            print("=" * 60)
            print()
            return self._load_mock(mock_file)

        try:
            return self.gemini.ask_json(prompt)

        except Exception as e:
            print()
            print("=" * 60)
            print("Gemini unavailable")
            print(e)
            print("Using Mock Data")
            print("=" * 60)
            print()
            return self._load_mock(mock_file)


provider = Provider()