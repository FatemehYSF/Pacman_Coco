"""Keyboard: what each key does on each screen."""
from typing import TYPE_CHECKING

import pygame

from pacman.highscores import (MAX_NAME, add_score, is_name_char,
                               save_scores)
from pacman.maze import EAST, NORTH, SOUTH, WEST
from pacman.ui.screens import MAIN_MENU, PAUSE_MENU

if TYPE_CHECKING:
    from pacman.ui.app import App

MOVE_KEYS = {pygame.K_UP: NORTH, pygame.K_w: NORTH,
             pygame.K_DOWN: SOUTH, pygame.K_s: SOUTH,
             pygame.K_LEFT: WEST, pygame.K_a: WEST,
             pygame.K_RIGHT: EAST, pygame.K_d: EAST}


def navigate(app: "App", key: int, count: int) -> int | None:
    """Move the menu cursor; return the chosen index on Enter."""
    if key in (pygame.K_UP, pygame.K_w):
        app.choice = (app.choice - 1) % count
    elif key in (pygame.K_DOWN, pygame.K_s):
        app.choice = (app.choice + 1) % count
    elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        return app.choice
    return None


def on_key(app: "App", event: pygame.event.Event) -> None:
    """Dispatch a key press to the current screen."""
    key = event.key
    if app.state == "menu":
        picked = navigate(app, key, len(MAIN_MENU))
        if picked == 0:
            app.start_game()
        elif picked is not None:
            app.state = ["menu", "highscores", "instructions",
                         "quit"][picked]
    elif app.state in ("highscores", "instructions"):
        if key in (pygame.K_ESCAPE, pygame.K_RETURN):
            app.state = "menu"
    elif app.state == "pause":
        picked = navigate(app, key, len(PAUSE_MENU))
        if picked == 0 or key == pygame.K_ESCAPE:
            app.state = "play"
        elif picked == 1:
            app.state, app.game, app.choice = "menu", None, 0
    elif app.state == "play":
        play_key(app, key)
    elif app.state == "name":
        name_key(app, event)


def play_key(app: "App", key: int) -> None:
    """Handle movement, pause and cheat keys during the game."""
    game = app.game
    if game is None:
        return
    if key in MOVE_KEYS:
        game.player.wanted = MOVE_KEYS[key]
    elif key in (pygame.K_p, pygame.K_ESCAPE):
        app.state, app.choice = "pause", 0
    elif key == pygame.K_c:
        game.toggle_cheat()
    elif game.cheat and key == pygame.K_i:
        game.invincible = not game.invincible
    elif game.cheat and key == pygame.K_f:
        game.frozen = not game.frozen
    elif game.cheat and key == pygame.K_v:
        game.fast = not game.fast
    elif game.cheat and key == pygame.K_l:
        game.lives += 1
    elif game.cheat and key == pygame.K_n:
        game.next_level()


def name_key(app: "App", event: pygame.event.Event) -> None:
    """Type the player name, then save the score on Enter."""
    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and app.game:
        app.scores = add_score(app.scores, app.name, app.game.score)
        save_scores(app.config["highscore_filename"], app.scores)
        app.state, app.game, app.choice = "menu", None, 0
    elif event.key == pygame.K_BACKSPACE:
        app.name = app.name[:-1]
    elif len(app.name) < MAX_NAME and is_name_char(event.unicode):
        app.name += event.unicode
