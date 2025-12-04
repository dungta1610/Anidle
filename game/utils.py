from __future__ import annotations
from typing import Dict, Any, List
from collections import Counter
import math

def median_of_range(r):
    if isinstance(r, (list, tuple)) and len(r) == 2:
        return (r[0] + r[1]) / 2.0
    return None

def letter_feedback(answer: str, guess: str) -> List[Dict[str,str]]:
    res = []
    a = list(answer)
    g = list(guess)
    cnt = Counter(a)
    for i, ch in enumerate(g):
        state = "absent"
        if i < len(a) and ch == a[i]:
            state = "correct"
            cnt[ch] -= 1
        res.append({"ch": ch, "state": state})
    for i, ch in enumerate(g):
        if res[i]["state"] == "correct":
            continue
        if cnt[ch] > 0:
            res[i]["state"] = "present"
            cnt[ch] -= 1
    return res

def trait_feedback(target: Dict[str, Any], guess: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    out["class"] = "match" if target.get("class") == guess.get("class") else "mismatch"
    out["diet"] = "match" if target.get("diet") == guess.get("diet") else "mismatch"

    th = set(target.get("habitat", []))
    gh = set(guess.get("habitat", []))
    out["habitat"] = {"matches": len(th & gh)}

    tc = set(target.get("continents", []))
    gc = set(guess.get("continents", []))
    out["continents"] = {"overlap": len(tc & gc)}

    def cmp_field(field, tol_percent=0.15):
    
        tr = median_of_range(target.get(field))
        gr = median_of_range(guess.get(field))
        if tr is None or gr is None:
            return {}

        tol = abs(tr) * tol_percent
        diff = tr - gr  

        if abs(diff) <= tol:
            return {"dir": "same"}
        return {"dir": "up" if diff > 0 else "down"}

    out["size"] = cmp_field("size_kg", tol_percent=0.2)
    out["lifespan"] = cmp_field("lifespan_years", tol_percent=0.2)
    return out

def sanitize_name(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalpha())
