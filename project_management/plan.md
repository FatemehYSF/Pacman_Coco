# Project management

## Timeline (Kanban)

| Step | Content | Status |
| --- | --- | --- |
| 1 | Read subject, install maze wheel, choose pygame-ce | done |
| 2 | Config loader + highscores (no graphics) | done |
| 3 | Maze wrapper + game rules (Game, Player, Ghost) | done |
| 4 | UI: menu, HUD, pause, name entry | done |
| 5 | Cheat mode, lint (flake8 + mypy strict) | done |
| 5b | Better UI: smooth movement, chomping Pac-Man, ghost eyes, HUD icons, menu animation | done |
| 5c | Split the UI into `pacman/ui/` (app, keys, screens, drawing) for easier review | done |
| 6 | Packaging + Itch.io upload | todo |
| 7 | Peer testing, bug fixes | todo |

## Choices

- pygame-ce instead of MLX: simplest drawing API and has Python 3.14 wheels.
- Grid movement (one cell per step): simple, no physics, easy to explain.
- Greedy ghost AI (Manhattan distance + a random-move chance per ghost:
  10 / 25 / 40 / 60 %), which gives each ghost a personality.
- Time up = lose a life (timer restarts).
- UI drawn only with pygame shapes: no image files to load or lose.
- UI split by question: `keys.py` = what a key does, `screens.py` = how a
  screen looks, `drawing.py` = how a thing looks, `app.py` = the loop. Plain
  functions taking `app`, no extra classes.

## Risks

| Risk | Mitigation |
| --- | --- |
| Maze package crashes or changes | every call wrapped, `MazeError` shown cleanly |
| Deep recursion in generator for big mazes | size clamped to 50, recursion limit raised |
| Center / corner cell inside the "42" block | use nearest open cell |
| Broken config or highscore file | defaults + clear messages |

## Acceptance tests

| Test | Result |
| --- | --- |
| Wrong number of arguments -> usage message | ok |
| Missing / broken config -> defaults | ok |
| Invalid values, out-of-range values, unknown keys | ok |
| Broken highscore file -> empty table; top 10 kept | ok |
| Name filtered to 10 alphanumeric/space chars | ok |
| All 10 levels generated and playable, win screen | ok |
| Game over after last life, lives never below 0 | ok (bug fixed) |
| Pause / resume / back to menu | ok |
| Each cheat key | ok |
| Top 3 scores on main menu | ok |
| `//` comments, new config keys | ok |
| UI split: 64 screenshots pixel-identical before / after | ok |
