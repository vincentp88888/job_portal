import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class ApplicationTracker:
    """Stores and loads application tracking entries to JSON."""

    def __init__(self, path: str = "data/applications.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return []

    def _write(self, data: List[Dict]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def list_applications(self) -> List[Dict]:
        return self._read()

    def add_application(self, entry: Dict) -> None:
        data = self._read()
        entry = entry.copy()
        entry.setdefault("applied_date", datetime.now().strftime("%Y-%m-%d"))
        data.append(entry)
        self._write(data)
