"""Load the JSON config file (with # or // comments) using safe defaults."""
import json
from typing import Any

DEFAULT_LEVELS: list[dict[str, int]] = [
    {"width": 15 + i, "height": 11 + i // 2} for i in range(10)
]
DEFAULTS: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 100,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 120,
    "frightened_duration": 7,
    "ghost_respawn_time": 5,
}
INT_RANGES: dict[str, tuple[int, int]] = {
    "lives": (1, 99),
    "pacgum": (1, 5000),
    "points_per_pacgum": (0, 100000),
    "points_per_super_pacgum": (0, 100000),
    "points_per_ghost": (0, 100000),
    "seed": (0, 2**31 - 1),
    "level_max_time": (10, 3600),
    "frightened_duration": (1, 60),
    "ghost_respawn_time": (1, 60),
}
MIN_SIZE, MAX_SIZE = 7, 50


def warn(message: str) -> None:
    """Print a configuration warning."""
    print(f"[config] {message}")


def read_json(path: str) -> Any:
    """Read a JSON file, ignoring lines starting with '#' or '//'."""
    try:
        with open(path, encoding="utf-8") as file:
            lines = [ln for ln in file
                     if not ln.lstrip().startswith(("#", "//"))]
        return json.loads("".join(lines))
    except OSError as error:
        warn(f"cannot read '{path}' ({error.strerror}), using defaults")
    except ValueError as error:
        warn(f"'{path}' is not valid JSON ({error}), using defaults")
    return {}


def get_int(data: dict[str, Any], key: str, default: int,
            low: int, high: int, where: str = "") -> int:
    """Return data[key] as an int clamped to [low, high], or the default."""
    value = data.get(key)
    if value is None:
        warn(f"missing '{where}{key}', using default {default}")
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        warn(f"invalid '{where}{key}' ({value!r}), using default {default}")
        return default
    number: int = value
    if not low <= number <= high:
        clamped = min(max(number, low), high)
        warn(f"'{where}{key}' out of range [{low}, {high}], using {clamped}")
        return clamped
    return number


def load_levels(value: Any) -> list[dict[str, int]]:
    """Validate the list of levels (width and height of each maze)."""
    if not isinstance(value, list) or not value:
        warn("missing or invalid 'levels', using 10 default levels")
        return DEFAULT_LEVELS
    levels: list[dict[str, int]] = []
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            warn(f"invalid 'levels[{i}]', using default size")
            item = {}
        where = f"levels[{i}]."
        levels.append({
            "width": get_int(item, "width", 15, MIN_SIZE, MAX_SIZE, where),
            "height": get_int(item, "height", 11, MIN_SIZE, MAX_SIZE, where),
        })
    return levels


def load_config(path: str) -> dict[str, Any]:
    """Load the configuration file and return a fully valid config dict."""
    data = read_json(path)
    if not isinstance(data, dict):
        warn("top-level JSON value must be an object, using defaults")
        data = {}
    config: dict[str, Any] = {}
    for key, (low, high) in INT_RANGES.items():
        config[key] = get_int(data, key, DEFAULTS[key], low, high)
    filename = data.get("highscore_filename")
    if not isinstance(filename, str) or not filename.strip():
        warn("missing or invalid 'highscore_filename', "
             f"using '{DEFAULTS['highscore_filename']}'")
        filename = DEFAULTS["highscore_filename"]
    config["highscore_filename"] = filename
    config["levels"] = load_levels(data.get("levels"))
    return config
