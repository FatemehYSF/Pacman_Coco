# Fatemeh & Ayda: meeting guide

Goal of the meeting: both of us can run the game, test it, and understand the
big picture before we go deep into the code. Then we decide together how
to divide the work.

---

## 1. How to run the project

```sh
git clone git@github.com:FatemehYSF/Pacman_fatemeh.git
cd Pacman_fatemeh
make install        # first time only: creates .venv, installs pygame-ce + maze wheel
make run            # = .venv/bin/python pac-man.py config.json
```

| Command | What it does |
| --- | --- |
| `make run` | start the game |
| `make lint` | flake8 + mypy (must show no errors) |
| `make debug` | run under pdb (type `c` + Enter to start) |
| `make clean` | delete caches and build files |
| `make package` | build `dist/pac-man-<os>.zip` for Itch.io |

**Controls:** arrows / WASD move, P / Esc pause, Enter in menus.
**Cheats:** press `C`, then `I` invincible, `F` freeze ghosts, `V` speed,
`L` +1 life, `N` skip level.

**Rules in short:** eat all dots → next level (10 levels). Big corner dots
turn ghosts blue for 7 s (you can eat them). Ghost touch or timer at 0 →
lose a life. 0 lives → GAME OVER. Level 10 cleared → YOU WIN. Then type a
name → highscore saved → main menu.

---

## 2. How to test it (do this together in the meeting)

Make a copy of the config for experiments: `cp config.json test.json`, then
run `.venv/bin/python pac-man.py test.json`.

### Command line
- [ ] no argument / two arguments → usage message, no crash
- [ ] file that does not exist → `[config]` message, game starts with defaults
- [ ] file that is not JSON (e.g. `README.md`) → message, defaults

### Config (edit `test.json`)
- [ ] remove `lives` → "missing", uses 3
- [ ] `"lives": "abc"` → invalid, uses 3
- [ ] `"lives": 1000` → clamped to 99
- [ ] `"levels": []` → 10 default levels
- [ ] `{"width": 1000, "height": 2}` → clamped to 50 x 7
- [ ] unknown key `"foo": 1` → ignored
- [ ] broken JSON (remove a comma) → message, defaults
- [ ] `#` and `//` comment lines → ignored
- [ ] `"pacgum": 10`, `"level_max_time": 30` → quick level for testing

### Highscores
- [ ] delete `highscores.json` → "No scores yet", file created after a game
- [ ] write garbage into it → starts empty, no crash
- [ ] name with `!@#` → those keys are ignored; max 10 characters
- [ ] empty name → saved as `PLAYER`
- [ ] more than 10 games → only top 10 kept
- [ ] top 3 visible on the main menu, all 10 on Highscores screen

### Gameplay
- [ ] walls block Pac-Man; pressing a direction early turns at next opening
- [ ] dot +10, big dot +50, blue ghost +200
- [ ] blue ghost eaten → comes back in its corner after 5 s
- [ ] ghost touch → -1 life, everybody back to start
- [ ] timer at 0 → -1 life, timer restarts
- [ ] all dots eaten → next level, score and lives kept
- [ ] pause → everything stops; Resume / Main Menu work
- [ ] close window or Ctrl+C at any time → no traceback

### Cheats and project
- [ ] every cheat key works only after `C`
- [ ] `C` + `N` x10 → YOU WIN screen
- [ ] `make lint` clean
- [ ] `make package`, unzip, `./pac-man config.json` works

---

## 3. Overall structure (big picture first)

```
pac-man.py              start: checks arguments, catches every error
pacman/
  config.py             reads config.json -> dict with safe values
  highscores.py         load / add / save the top 10
  maze.py               Maze: wraps the external mazegenerator package
  entities.py           Player and Ghost (ghost AI = choose_direction)
  game.py               Game: rules (levels, dots, score, lives, timer, cheats)
  ui.py                 App: window, main loop, screens, drawing
project_management/     plan, diagrams, this file
```

**Who talks to whom**

```
pac-man.py ──> config.py
     │
     └──> ui.py (App) ──> highscores.py
              │
              └──> game.py (Game) ──> maze.py ──> mazegenerator package
                        │
                        └──> entities.py (Player, Ghost)
```

**How one frame works (60 times per second)**

1. `App.run` reads the keyboard.
2. If we are playing: `Game.update(dt)` moves the player and ghosts when
   their step timer is ready, eats dots, checks collisions, timer, level end.
3. `App.draw` draws the current screen (menu, game, pause, name entry...).

**Screens** are just a string `App.state`:
`menu → play ⇄ pause`, `play → name → menu`, `menu → highscores / instructions`.

Key idea: only `ui.py` uses pygame. All the rules are in `game.py`, so the
logic can be tested without a window.

More pictures: `project_management/diagrams.md`.

---

## 4. Task split: to discuss together

Nothing is decided yet. Some points to talk about:

**The code falls naturally into two halves**, if we want to split:

| Half | Files | Topics |
| --- | --- | --- |
| Game logic (the "brain") | `maze.py`, `entities.py`, `game.py` | maze package + wall bits, player movement, ghost AI, eating, score, lives, timer, levels, cheats |
| Program, files and screen (the "body") | `pac-man.py`, `config.py`, `highscores.py`, `ui.py`, `Makefile`, `package.sh` | arguments + error handling, config validation, highscores, main loop, screens, drawing, packaging |

**Questions for the meeting**
- Do we split the code in two halves, or go through every file together?
- If we split: who takes which half, and when do we teach each other?
- Who writes which README sections? (Description, Instructions, Configuration,
  Highscores, Maze Generation, Implementation, Architecture, Project
  Management, Resources + AI usage)
- Who does the Itch.io upload, and who builds the Linux package on a school
  computer?
- How do we divide the testing checklist (section 2)?
- How do we keep `plan.md` up to date (the subject asks for "who did what")?

**Whatever we choose**, at the peer review **both** of us must be able to
explain every file. Good checks, one for each half:
- How does a ghost choose its way? What does a big dot do? Why is level 1
  always the same maze? What if the maze package crashes?
- What happens with a broken config? How is the name `"a!b@c"` saved? How do
  screens change? How is movement smooth if the logic moves cell by cell? How
  do we rebuild the Itch.io package?

---

## 5. Plan until the review (proposal)

| When | What |
| --- | --- |
| Meeting 1 | run + test together (sections 1–3), decide how to divide the work |
| Next days | study the code; change small things to see the effect (ghost `randomness`, a colour, a config value) |
| Then | explain the code to each other |
| Then | practice "recode" tasks, e.g. faster ghosts when 1 life is left, a new config key `ghost_speed`, a new cheat key |
| Before review | answer each other's questions without looking at the code |

## 6. Open points
- [ ] Put both logins on the first line of `README.md`
- [ ] Rewrite the AI usage paragraph in our own words
- [ ] Upload the package to Itch.io (unlisted) and add the link to the README
- [ ] Run the whole checklist on a school (Linux) computer
