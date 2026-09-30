"""Screens: menu, highscores, instructions, game + HUD, pause, name entry."""
from typing import TYPE_CHECKING

import pygame

from pacman.game import Game
from pacman.maze import EAST
from pacman.ui.drawing import (BLACK, DOT, GREY, HEIGHT, HUD, RED, WALL,
                               WHITE, WIDTH, YELLOW, Color, draw_board,
                               draw_ghost, draw_pacman, ticks)

if TYPE_CHECKING:
    from pacman.ui.app import App

MENU_GHOSTS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
MAIN_MENU = ["Start Game", "Highscores", "Instructions", "Exit"]
PAUSE_MENU = ["Resume", "Main Menu"]
INSTRUCTIONS = [
    ("Arrows / WASD", "move"),
    ("P / Esc", "pause"),
    ("Small dots", "eat them all to clear the level"),
    ("Big dots", "ghosts turn blue: eat them!"),
    ("Ghost / time up", "you lose a life"),
    ("", ""),
    ("C", "toggle cheat mode, then:"),
    ("I / F / V", "invincible / freeze ghosts / speed"),
    ("L / N", "extra life / skip level"),
]


def text(app: "App", text: str, pos: tuple[int, int], color: Color = WHITE,
         font: pygame.font.Font | None = None,
         anchor: str = "center") -> None:
    """Draw text with the given anchor point (center, midleft...)."""
    surface = (font or app.font).render(text, True, color)
    app.screen.blit(surface, surface.get_rect(**{anchor: pos}))


def title(app: "App", label: str, color: Color = YELLOW) -> None:
    """Draw a big screen title with a thin line under it."""
    text(app, label, (WIDTH // 2, 90), color, app.big)
    pygame.draw.line(app.screen, WALL, (160, 140), (WIDTH - 160, 140), 3)


def menu(app: "App", items: list[str], y: int) -> None:
    """Draw a vertical menu; the selected item has a Pac-Man cursor."""
    for i, item in enumerate(items):
        selected = i == app.choice
        text(app, item, (WIDTH // 2, y + i * 56),
             YELLOW if selected else GREY)
        if selected:
            draw_pacman(app.screen, (WIDTH // 2 - 150, y + i * 56),
                        13, EAST)


def draw_screen(app: "App") -> None:
    """Draw the current screen."""
    app.screen.fill(BLACK)
    footer = (WIDTH // 2, HEIGHT - 30)
    if app.state == "menu":
        draw_menu(app)
    elif app.state == "highscores":
        title(app, "HIGHSCORES")
        for i, (name, score) in enumerate(app.scores):
            color = YELLOW if i == 0 else WHITE
            text(app, f"{i + 1:>2}.  {name:<10}  {score:>7}",
                 (WIDTH // 2, 190 + i * 38), color)
        if not app.scores:
            text(app, "No scores yet", (WIDTH // 2, 240), GREY)
        text(app, "Esc  back", footer, GREY, app.small)
    elif app.state == "instructions":
        title(app, "HOW TO PLAY")
        for i, (keys, action) in enumerate(INSTRUCTIONS):
            y = 190 + i * 40
            text(app, keys, (340, y), YELLOW, app.small, "midright")
            text(app, action, (360, y), WHITE, app.small, "midleft")
        text(app, "Esc  back", footer, GREY, app.small)
    elif app.state in ("play", "pause") and app.game:
        draw_hud(app, app.game)
        draw_board(app.screen, app.game)
        if app.state == "pause":
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 180))
            app.screen.blit(shade, (0, 0))
            text(app, "PAUSED", (WIDTH // 2, 250), YELLOW, app.big)
            menu(app, PAUSE_MENU, 340)
    elif app.state == "name" and app.game:
        draw_end(app, app.game)


def draw_menu(app: "App") -> None:
    """Draw the main menu with a small Pac-Man chase animation."""
    text(app, "PAC-MAN", (WIDTH // 2, 120), YELLOW, app.big)
    x = (ticks() * 150) % (WIDTH + 400) - 200
    for i in range(12):
        dot_x = 60 + i * 60
        if dot_x > x:
            pygame.draw.circle(app.screen, DOT, (dot_x, 210), 4)
    draw_pacman(app.screen, (x, 210), 18, EAST)
    for i, color in enumerate(MENU_GHOSTS):
        draw_ghost(app.screen, (x - 60 - i * 45, 210), 18, color, EAST)
    menu(app, MAIN_MENU, 290)
    text(app, "TOP 3", (WIDTH // 2, 510), YELLOW, app.small)
    for i, (name, score) in enumerate(app.scores[:3]):
        text(app, f"{i + 1}. {name:<10} {score:>7}",
             (WIDTH // 2, 540 + i * 24), WHITE, app.small)
    if not app.scores:
        text(app, "No scores yet", (WIDTH // 2, 540), GREY, app.small)
    if app.message:
        text(app, app.message, (WIDTH // 2, 605), RED, app.small)
    text(app, "Arrows + Enter", (WIDTH // 2, HEIGHT - 30), GREY, app.small)


def draw_end(app: "App", game: Game) -> None:
    """Draw the game over / victory screen with the name input."""
    if game.won:
        title(app, "YOU WIN!")
        text(app, "Congratulations, every level cleared!",
             (WIDTH // 2, 190), WHITE, app.small)
    else:
        title(app, "GAME OVER", RED)
    text(app, f"FINAL SCORE  {game.score}", (WIDTH // 2, 260))
    text(app, "Enter your name", (WIDTH // 2, 350), GREY, app.small)
    box = pygame.Rect(WIDTH // 2 - 150, 375, 300, 50)
    pygame.draw.rect(app.screen, WALL, box, 3, border_radius=8)
    cursor = "_" if int(ticks() * 2) % 2 else " "
    text(app, app.name + cursor, box.center, YELLOW)
    text(app, "Enter  save", (WIDTH // 2, HEIGHT - 30), GREY, app.small)


def draw_hud(app: "App", game: Game) -> None:
    """Draw score, lives, level, cheats and time at the top."""
    y = HUD // 2
    text(app, f"SCORE {game.score}", (16, y), WHITE, app.small, "midleft")
    for i in range(min(game.lives, 8)):
        draw_pacman(app.screen, (200 + i * 24, y), 9, EAST)
    text(app, f"LEVEL {game.level + 1}/{len(app.config['levels'])}",
         (WIDTH // 2 + 40, y), WHITE, app.small)
    if game.cheat:
        flags = "I" * game.invincible + "F" * game.frozen + \
            "V" * game.fast
        text(app, f"CHEAT {flags}", (WIDTH - 130, y), RED, app.small,
             "midright")
    time_color = RED if game.time_left < 10 else WHITE
    text(app, f"TIME {int(game.time_left)}", (WIDTH - 16, y),
         time_color, app.small, "midright")
