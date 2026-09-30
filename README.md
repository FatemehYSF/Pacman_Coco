*This project has been created as part of the 42 curriculum by <fyousefi> and <ayafshar>.*

# Pac-Man

## Description

A small, complete Pac-Man clone in Python using pygame-ce. The mazes come from
the external A-Maze-ing package `mazegenerator`. The game has 10 levels, a
time limit per level, edible ghosts, a highscore table, a pause menu and a
cheat mode that helps with peer review.

## Instructions

```sh
make install     # create .venv, install pygame-ce, flake8, mypy and the maze wheel
make run         # python3 pac-man.py config.json
make debug       # same, under pdb
make lint        # flake8 + mypy
make clean       # remove caches and build files
make package     # build dist/pac-man-<os>.zip (PyInstaller)
```

Usage: `python3 pac-man.py <config.json>` (exactly one argument).

| Key | Action |
| --- | --- |
| Arrows / WASD | move |
| P / Esc | pause (Resume / Main Menu) |
| Enter | select in menus |
| C | toggle cheat mode |
| I / F / V / L / N | (cheat) invincible / freeze ghosts / speed / +1 life / skip level |

Rules: eat every pacgum to clear a level. The big pacgums in the 4 corners make
ghosts edible for 7 s (`frightened_duration`). An eaten ghost comes back to its
corner after 5 s (`ghost_respawn_time`).
Touching a normal ghost, or running out of time, costs one life. After the last
level (win) or the last life (game over) you type your name and go back to the
main menu.

## Configuration

`config.json` is JSON where lines starting with `#` or `//` are comments. Unknown keys
are ignored. Missing or invalid values print a `[config]` message and use the
default; numbers out of range are clamped. An unreadable or broken file means
all defaults.

| Key | Default | Range / meaning |
| --- | --- | --- |
| `highscore_filename` | `"highscores.json"` | non-empty string |
| `lives` | 3 | 1 – 99 |
| `pacgum` | 100 | 1 – 5000, max pacgums per level |
| `points_per_pacgum` | 10 | 0 – 100000 |
| `points_per_super_pacgum` | 50 | 0 – 100000 |
| `points_per_ghost` | 200 | 0 – 100000 |
| `seed` | 42 | seed of level 1 (0 = random); next levels are random |
| `level_max_time` | 120 | 10 – 3600 seconds |
| `frightened_duration` | 7 | 1 – 60 seconds ghosts stay edible |
| `ghost_respawn_time` | 5 | 1 – 60 seconds before an eaten ghost returns |
| `levels` | 10 levels, 15x11 to 24x15 | list of `{"width", "height"}`, 7 – 50 each |

## Highscores

Stored in the JSON file `highscore_filename` as a list of
`{"name": str, "score": int}`. It is loaded when the game starts and saved after
the player enters a name. The main menu shows the top 3; the Highscores screen
shows all 10. Only the top 10 are kept. Names keep only ASCII
letters, digits and spaces, max 10 characters (empty becomes `PLAYER`).
Invalid entries, a missing file or bad JSON are ignored (empty table), and a
failed save prints a message instead of crashing. JSON was chosen because it is
human readable, easy to reset and needs no extra library.

## Maze Generation

`pacman/maze.py` calls the package as-is:
`MazeGenerator(size=(width, height), perfect=False, seed=seed)` and reads
`.maze`, a grid of ints where bits are walls (N=1, E=2, S=4, W=8). A cell with
value 15 is a solid block (the "42" pattern) and is drawn filled. Moving from
one cell to its neighbour is allowed when neither cell has a wall on that side.
The player starts on the open cell nearest to the center and the ghosts and
super-pacgums on the open cells nearest to the 4 corners. Any exception from
the generator becomes a `MazeError`: the error is shown in the menu (or ends the
game), never as a traceback.

## Implementation

- Movement is grid based: the player moves one cell every 0.15 s (half with
  the speed cheat), ghosts every 0.35 s (0.7 s when edible).
- The player keeps a *wanted* direction and turns as soon as the corridor allows.
- Ghost AI: at each cell a ghost looks at the open directions (no U-turn unless
  it is a dead end) and takes the one that minimises the Manhattan distance to
  the player (chase) or maximises it (flee when edible). Each ghost has its
  own chance of a random move, which gives it a personality: red 10 %
  (hunter), pink 25 %, cyan 40 %, orange 60 % (wanderer).
- Collisions are checked after every move. Losing a life resets the player and
  the ghosts; running out of time costs a life and restarts the timer.
- All screens are states of one loop (`menu`, `highscores`, `instructions`,
  `play`, `pause`, `name`, `quit`).

## General Software Architecture

```
pac-man.py            entry point: checks argv, catches every error
pacman/config.py      load_config(): JSON + # comments -> validated dict
pacman/highscores.py  load_scores / add_score / save_scores
pacman/maze.py        Maze: wraps MazeGenerator, walls, can_move, center, corners
pacman/entities.py    Player, Ghost (Ghost.choose_direction = AI)
pacman/game.py        Game: levels, pacgums, score, lives, timers, cheats
pacman/ui.py          App: pygame window, key handling, drawing of every screen
```

`App` owns the config, the highscores and the current `Game`. `Game` owns a
`Maze`, a `Player` and 4 `Ghost`s. Only `ui.py` imports pygame, so the game
rules can be tested without a window.

## Packaging

`make package` runs `package.sh`: PyInstaller builds a standalone folder (`pac-man` + `_internal/`),
then it is zipped with `config.json`, `highscores.json` and `PLAY.txt`
(in-package instructions) into `dist/pac-man-<os>.zip`, ready to upload to
Itch.io as an unlisted build.

## Project Management

See [project_management/](project_management/): `plan.md` (timeline, choices,
risks, acceptance tests) and `diagrams.md` (screens, game loop, modules, ghost
AI).
Team meeting guide (run, test, structure, work division): `Fatemeh_Ayda.md`.

## Resources

- pygame-ce documentation: https://pyga.me/docs/
- Pac-Man ghost behaviour: https://gameinternals.com/understanding-pac-man-ghost-behavior
- PyInstaller manual: https://pyinstaller.org/
- mypy and flake8 documentation

AI usage: an AI assistant (Claude) was used to draft the first version of the
code structure, the Makefile, the packaging script and this README. Every part
was then read, tested and adjusted by hand.
