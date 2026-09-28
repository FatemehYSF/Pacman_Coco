"""Load and save the top 10 highscores in a JSON file."""
import json
from typing import Any

MAX_SCORES = 10
MAX_NAME = 10
Score = tuple[str, int]


def is_name_char(char: str) -> bool:
    """Return True if char is allowed in a player name."""
    return char == " " or (char.isascii() and char.isalnum())


def clean_name(name: str) -> str:
    """Keep only allowed characters, max 10 of them."""
    name = "".join(c for c in name if is_name_char(c))[:MAX_NAME].strip()
    return name or "PLAYER"


def add_score(scores: list[Score], name: str, score: int) -> list[Score]:
    """Insert a score and keep only the best 10."""
    scores = scores + [(clean_name(name), max(0, score))]
    return sorted(scores, key=lambda s: s[1], reverse=True)[:MAX_SCORES]


def load_scores(path: str) -> list[Score]:
    """Load highscores from disk. Bad or missing files give an empty list."""
    try:
        with open(path, encoding="utf-8") as file:
            data: Any = json.load(file)
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as error:
        print(f"[highscores] cannot load '{path}' ({error}), starting empty")
        return []
    scores: list[Score] = []
    for item in data if isinstance(data, list) else []:
        if not isinstance(item, dict):
            continue
        name, score = item.get("name"), item.get("score")
        if (isinstance(name, str) and isinstance(score, int)
                and not isinstance(score, bool) and score >= 0):
            scores = add_score(scores, name, score)
    return scores


def save_scores(path: str, scores: list[Score]) -> None:
    """Write highscores to disk."""
    data = [{"name": name, "score": score} for name, score in scores]
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError as error:
        print(f"[highscores] cannot save '{path}' ({error.strerror})")
