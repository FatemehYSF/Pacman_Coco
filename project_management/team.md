# Team organization

Team: **fyousefi** (Fatemeh) and **ayafshar** (Ayda).

## How we worked

- **Online meetings on Google Meet, almost every day.** Most of the work was
  done together in these sessions, sharing the screen: one person typed, the
  other followed, asked questions and checked.
- **Git + GitHub** for the code. Changes were tested (`make run`, `make lint`)
  before being pushed to `main`.
- **Fair task division:** instead of each person owning half of the code, we
  worked on every part together, so both of us know the whole project. At the
  peer review either of us can explain any file.

## Who did what

| Part | Files | Who |
| --- | --- | --- |
| Reading the subject, planning the architecture | — | both, together |
| Config loader | `pacman/config.py`, `config.json` | both, together |
| Highscores | `pacman/highscores.py` | both, together |
| Maze integration | `pacman/maze.py` | both, together |
| Player and ghost AI | `pacman/entities.py` | both, together |
| Game rules | `pacman/game.py` | both, together |
| User interface | `pacman/ui/` | both, together |
| Entry point and error handling | `pac-man.py` | both, together |
| Makefile, lint, packaging | `Makefile`, `setup.cfg`, `package.sh` | both, together |
| Testing (see `plan.md`) | — | both, together |
| README and project management | `README.md`, `project_management/` | both, together |
| Itch.io upload (macOS + Linux) | — | both, together |

## How decisions were made

We discussed each choice during the meetings and picked the simplest option
that meets the subject, so the code stays easy to explain and to change.

Main decisions:

- **pygame-ce** instead of MLX: simplest drawing API, works on Python 3.14.
- **Grid movement**, one cell per step: no physics, easy to explain.
- **Greedy ghost AI** (Manhattan distance) with a different random-move
  chance per ghost, which gives each ghost a personality.
- **Time up = lose a life**, then the timer restarts.
- **UI drawn only with shapes** (no image files), split into `pacman/ui/`
  (`app`, `keys`, `screens`, `drawing`) to make reviewing easier.

## Problems and how we handled them

| Problem | What we did |
| --- | --- |
| The one-file package was killed by macOS on launch | switched PyInstaller to `--onedir` (a folder) |
| The game was too hard: fast ghosts, too many pacgums for the time | slower ghosts, max 100 pacgums, 120 s per level |
| `mypy` errors when run with the system Python 3.9 | set `python_version = 3.10` in `setup.cfg` |
| Lives could go below 0 when two ghosts touched Pac-Man at once | `lose_life` does nothing once the game is over |
| VS Code showed errors in `config.json` | normal: `#` comments are not standard JSON, the subject requires them |
| Itch.io security check did not load | retried later / other browser |

## Use of AI

We used an AI assistant (Claude) as a tool during the project:

- to read and understand the subject and the algorithms behind the game
  (grid movement, wall bits, the greedy ghost AI, time steps with `dt`);
- to produce a first version of the code from the subject's requirements;
- to split the code into small pieces (for example the UI into `app`, `keys`,
  `screens`, `drawing`), improve the drawing and movement of Pac-Man and the
  ghosts, and fix lint and mypy errors;
- to explain the code and help us write the documentation.

We did not keep anything we did not understand. Together, in our online
meetings, we read every file, tested it, changed it (difficulty, config, UI,
project files), and checked it against the subject. We can explain and modify
every part of the code ourselves.
