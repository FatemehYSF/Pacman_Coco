"""Pac-Man entry point. Usage: python3 pac-man.py config.json"""
import os
import sys


def main() -> int:
    """Check the arguments, load the config and run the game."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>")
        return 1
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    try:
        from pacman.config import load_config
        from pacman.ui import App
        App(load_config(sys.argv[1])).run()
    except ImportError as error:
        print(f"Error: missing module '{error.name}'. Run 'make install'.")
        return 1
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
