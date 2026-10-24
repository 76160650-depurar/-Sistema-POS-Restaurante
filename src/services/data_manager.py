
import json
from pathlib import Path
from typing import Any


class DataManager:
    def __init__(self, path: str = "data/restaurant.json"):
        self.path = Path(path)

    def save(self, payload: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def exists(self) -> bool:
        return self.path.exists()
