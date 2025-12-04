from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, Any, List

DATA_DIR = Path(__file__).resolve().parent / "data"
ANIMALS_FILE = DATA_DIR / "animals.json"

class AnimalDB:
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.by_name: Dict[str, Dict[str, Any]] = {}

    def load(self):
        raw = json.loads(ANIMALS_FILE.read_text(encoding="utf-8"))
        self.items = raw
        self.by_name = {}
        for a in self.items:
            nm = a["name_en"]
            nm_key = normalize(nm)
            self.by_name[nm_key] = a

    def search(self, q: str, limit: int = 25) -> List[str]:
        qn = normalize(q)
        if not qn:
            return [a["name_en"] for a in self.items[:limit]]
        out = []
        for a in self.items:
            nm = a["name_en"]
            if qn in normalize(nm):
                out.append(nm)
                if len(out) >= limit: break
        return out

    def get(self, name: str) -> Dict[str, Any] | None:
        return self.by_name.get(normalize(name))

def normalize(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("-", " ")
    s = " ".join([w for w in s.split() if w])
    return s
