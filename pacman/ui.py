"""Window, screens (menu, game, pause, name entry) and drawing."""
import math
from typing import Any

import pygame

from pacman.game import Game
from pacman.highscores import (MAX_NAME, add_score, is_name_char,
                               load_scores, save_scores)
from pacman.maze import CLOSED, DIRS, EAST, NORTH, SOUTH, WEST, Cell, \
    MazeError

WIDTH, HEIGHT, HUD = 800, 660, 60
Color = tuple[int, int, int]
BLACK, WHITE, GREY = (0, 0, 0), (255, 255, 255), (140, 140, 160)
WALL, BLOCK = (40, 60, 255), (15, 20, 90)
YELLOW, RED, DOT = (255, 225, 0), (255, 70, 70), (255, 184, 151)
SCARED, SCARED_FACE = (40, 40, 220), (255, 184, 151)
MENU_GHOSTS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
MAIN_MENU = ["Start Game", "Highscores", "Instructions", "Exit"]
PAUSE_MENU = ["Resume", "Main Menu"]
ANGLES = {0: 0, EAST: 0, NORTH: 90, WEST: 180, SOUTH: 270}
MOVE_KEYS = {pygame.K_UP: NORTH, pygame.K_w: NORTH,
             pygame.K_DOWN: SOUTH, pygame.K_s: SOUTH,
             pygame.K_LEFT: WEST, pygame.K_a: WEST,
             pygame.K_RIGHT: EAST, pygame.K_d: EAST}
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


def ticks() -> float:
    """Seconds since pygame started (used for simple animations)."""
    return pygame.time.get_ticks() / 1000


def draw_pacman(screen: pygame.Surface, pos: tuple[float, float],
                radius: float, direction: int) -> None:
    """Draw Pac-Man with a chomping mouth facing its direction."""
    pygame.draw.circle(screen, YELLOW, pos, radius)
    mouth = math.radians(5 + 40 * abs(math.sin(ticks() * 10)))
    angle = math.radians(ANGLES[direction])
    points = [pos]
    for a in (angle - mouth, angle + mouth):
        points.append((pos[0] + math.cos(a) * radius * 1.1,
                       pos[1] - math.sin(a) * radius * 1.1))
    pygame.draw.polygon(screen, BLACK, points)


def draw_ghost(screen: pygame.Surface, pos: tuple[float, float],
               radius: float, color: Color, direction: int,
               scared: bool = False) -> None:
    """Draw a ghost: round head, wavy skirt and eyes looking ahead."""
    x, y = pos
    pygame.draw.circle(screen, color, (x, y), radius)
    screen.fill(color, (x - radius, y, radius * 2, radius * 0.7))
    for i in range(3):
        pygame.draw.circle(screen, color, (x - radius * 2 / 3 * (1 - i),
                                           y + radius * 0.7), radius / 3)
    if scared:
        for dx in (-0.35, 0.35):
            pygame.draw.circle(screen, SCARED_FACE,
                               (x + dx * radius, y - radius * 0.2),
                               radius * 0.15)
        return
    dx, dy = DIRS.get(direction, (0, 0))
    for side in (-0.38, 0.38):
        eye = (x + side * radius, y - radius * 0.2)
        pygame.draw.circle(screen, WHITE, eye, radius * 0.28)
        pygame.draw.circle(screen, (30, 30, 200),
                           (eye[0] + dx * radius * 0.12,
                            eye[1] + dy * radius * 0.12), radius * 0.14)


class App:
    """The application: one loop, one current screen (state)."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Open the window and load the highscores."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        mono = "menlo,consolas,dejavusansmono,couriernew"
        self.big = pygame.font.SysFont(mono, 64, bold=True)
        self.font = pygame.font.SysFont(mono, 28, bold=True)
        self.small = pygame.font.SysFont(mono, 18, bold=True)
        self.config = config
        self.scores = load_scores(config["highscore_filename"])
        self.state = "menu"
        self.choice = 0
        self.game: Game | None = None
        self.name = ""
        self.message = ""

    def run(self) -> None:
        """Main loop: events, update, draw, until the player quits."""
        while self.state != "quit":
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "quit"
                elif event.type == pygame.KEYDOWN:
                    self.on_key(event)
            if self.state == "play" and self.game:
                self.game.update(dt)
                if self.game.over:
                    self.state, self.name = "name", ""
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def start_game(self) -> None:
        """Create a new game, or show an error if the maze fails."""
        try:
            self.game = Game(self.config)
            self.state, self.message = "play", ""
        except MazeError as error:
            self.message = str(error)
            print(f"Error: {error}")

    def navigate(self, key: int, count: int) -> int | None:
        """Move the menu cursor; return the chosen index on Enter."""
        if key in (pygame.K_UP, pygame.K_w):
            self.choice = (self.choice - 1) % count
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.choice = (self.choice + 1) % count
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return self.choice
        return None

    def on_key(self, event: pygame.event.Event) -> None:
        """Dispatch a key press to the current screen."""
        key = event.key
        if self.state == "menu":
            picked = self.navigate(key, len(MAIN_MENU))
            if picked == 0:
                self.start_game()
            elif picked is not None:
                self.state = ["menu", "highscores", "instructions",
                              "quit"][picked]
        elif self.state in ("highscores", "instructions"):
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.state = "menu"
        elif self.state == "pause":
            picked = self.navigate(key, len(PAUSE_MENU))
            if picked == 0 or key == pygame.K_ESCAPE:
                self.state = "play"
            elif picked == 1:
                self.state, self.game, self.choice = "menu", None, 0
        elif self.state == "play":
            self.play_key(key)
        elif self.state == "name":
            self.name_key(event)

    def play_key(self, key: int) -> None:
        """Handle movement, pause and cheat keys during the game."""
        game = self.game
        if game is None:
            return
        if key in MOVE_KEYS:
            game.player.wanted = MOVE_KEYS[key]
        elif key in (pygame.K_p, pygame.K_ESCAPE):
            self.state, self.choice = "pause", 0
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

    def name_key(self, event: pygame.event.Event) -> None:
        """Type the player name, then save the score on Enter."""
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.game:
            self.scores = add_score(self.scores, self.name, self.game.score)
            save_scores(self.config["highscore_filename"], self.scores)
            self.state, self.game, self.choice = "menu", None, 0
        elif event.key == pygame.K_BACKSPACE:
            self.name = self.name[:-1]
        elif len(self.name) < MAX_NAME and is_name_char(event.unicode):
            self.name += event.unicode

    def text(self, text: str, pos: tuple[int, int], color: Color = WHITE,
             font: pygame.font.Font | None = None,
             anchor: str = "center") -> None:
        """Draw text with the given anchor point (center, midleft...)."""
        surface = (font or self.font).render(text, True, color)
        self.screen.blit(surface, surface.get_rect(**{anchor: pos}))

    def title(self, text: str, color: Color = YELLOW) -> None:
        """Draw a big screen title with a thin line under it."""
        self.text(text, (WIDTH // 2, 90), color, self.big)
        pygame.draw.line(self.screen, WALL, (160, 140), (WIDTH - 160, 140), 3)

    def menu(self, items: list[str], y: int) -> None:
        """Draw a vertical menu; the selected item has a Pac-Man cursor."""
        for i, item in enumerate(items):
            selected = i == self.choice
            self.text(item, (WIDTH // 2, y + i * 56),
                      YELLOW if selected else GREY)
            if selected:
                draw_pacman(self.screen, (WIDTH // 2 - 150, y + i * 56),
                            13, EAST)

    def draw(self) -> None:
        """Draw the current screen."""
        self.screen.fill(BLACK)
        footer = (WIDTH // 2, HEIGHT - 30)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "highscores":
            self.title("HIGHSCORES")
            for i, (name, score) in enumerate(self.scores):
                color = YELLOW if i == 0 else WHITE
                self.text(f"{i + 1:>2}.  {name:<10}  {score:>7}",
                          (WIDTH // 2, 190 + i * 38), color)
            if not self.scores:
                self.text("No scores yet", (WIDTH // 2, 240), GREY)
            self.text("Esc  back", footer, GREY, self.small)
        elif self.state == "instructions":
            self.title("HOW TO PLAY")
            for i, (keys, action) in enumerate(INSTRUCTIONS):
                y = 190 + i * 40
                self.text(keys, (340, y), YELLOW, self.small, "midright")
                self.text(action, (360, y), WHITE, self.small, "midleft")
            self.text("Esc  back", footer, GREY, self.small)
        elif self.state in ("play", "pause") and self.game:
            self.draw_game(self.game)
            if self.state == "pause":
                shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                shade.fill((0, 0, 0, 180))
                self.screen.blit(shade, (0, 0))
                self.text("PAUSED", (WIDTH // 2, 250), YELLOW, self.big)
                self.menu(PAUSE_MENU, 340)
        elif self.state == "name" and self.game:
            self.draw_end(self.game)

    def draw_menu(self) -> None:
        """Draw the main menu with a small Pac-Man chase animation."""
        self.text("PAC-MAN", (WIDTH // 2, 120), YELLOW, self.big)
        x = (ticks() * 150) % (WIDTH + 400) - 200
        for i in range(12):
            dot_x = 60 + i * 60
            if dot_x > x:
                pygame.draw.circle(self.screen, DOT, (dot_x, 210), 4)
        draw_pacman(self.screen, (x, 210), 18, EAST)
        for i, color in enumerate(MENU_GHOSTS):
            draw_ghost(self.screen, (x - 60 - i * 45, 210), 18, color, EAST)
        self.menu(MAIN_MENU, 290)
        self.text("TOP 3", (WIDTH // 2, 510), YELLOW, self.small)
        for i, (name, score) in enumerate(self.scores[:3]):
            self.text(f"{i + 1}. {name:<10} {score:>7}",
                      (WIDTH // 2, 540 + i * 24), WHITE, self.small)
        if not self.scores:
            self.text("No scores yet", (WIDTH // 2, 540), GREY, self.small)
        if self.message:
            self.text(self.message, (WIDTH // 2, 605), RED, self.small)
        self.text("Arrows + Enter", (WIDTH // 2, HEIGHT - 30), GREY,
                  self.small)

    def draw_end(self, game: Game) -> None:
        """Draw the game over / victory screen with the name input."""
        if game.won:
            self.title("YOU WIN!")
            self.text("Congratulations, every level cleared!",
                      (WIDTH // 2, 190), WHITE, self.small)
        else:
            self.title("GAME OVER", RED)
        self.text(f"FINAL SCORE  {game.score}", (WIDTH // 2, 260))
        self.text("Enter your name", (WIDTH // 2, 350), GREY, self.small)
        box = pygame.Rect(WIDTH // 2 - 150, 375, 300, 50)
        pygame.draw.rect(self.screen, WALL, box, 3, border_radius=8)
        cursor = "_" if int(ticks() * 2) % 2 else " "
        self.text(self.name + cursor, box.center, YELLOW)
        self.text("Enter  save", (WIDTH // 2, HEIGHT - 30), GREY, self.small)

    def draw_hud(self, game: Game) -> None:
        """Draw score, lives, level, cheats and time at the top."""
        y = HUD // 2
        self.text(f"SCORE {game.score}", (16, y), WHITE, self.small,
                  "midleft")
        for i in range(min(game.lives, 8)):
            draw_pacman(self.screen, (200 + i * 24, y), 9, EAST)
        self.text(f"LEVEL {game.level + 1}/{len(self.config['levels'])}",
                  (WIDTH // 2 + 40, y), WHITE, self.small)
        if game.cheat:
            flags = "I" * game.invincible + "F" * game.frozen + \
                "V" * game.fast
            self.text(f"CHEAT {flags}", (WIDTH - 130, y), RED, self.small,
                      "midright")
        time_color = RED if game.time_left < 10 else WHITE
        self.text(f"TIME {int(game.time_left)}", (WIDTH - 16, y),
                  time_color, self.small, "midright")

    def draw_game(self, game: Game) -> None:
        """Draw the HUD, the maze, the pacgums, the player and the ghosts."""
        maze = game.maze
        cell = min((WIDTH - 24) // maze.width,
                   (HEIGHT - HUD - 16) // maze.height)
        left = (WIDTH - cell * maze.width) // 2
        top = HUD + (HEIGHT - HUD - cell * maze.height) // 2

        def center(c: Cell) -> tuple[int, int]:
            return (left + c[0] * cell + cell // 2,
                    top + c[1] * cell + cell // 2)

        def between(a: Cell, b: Cell, t: float) -> tuple[float, float]:
            (ax, ay), (bx, by), t = center(a), center(b), min(t, 1.0)
            return ax + (bx - ax) * t, ay + (by - ay) * t

        self.draw_hud(game)
        for y, row in enumerate(maze.grid):
            for x, walls in enumerate(row):
                x0, y0 = left + x * cell, top + y * cell
                x1, y1 = x0 + cell, y0 + cell
                if walls == CLOSED:
                    self.screen.fill(BLOCK, (x0, y0, cell, cell))
                    continue
                for bit, a, b in ((NORTH, (x0, y0), (x1, y0)),
                                  (EAST, (x1, y0), (x1, y1)),
                                  (SOUTH, (x0, y1), (x1, y1)),
                                  (WEST, (x0, y0), (x0, y1))):
                    if walls & bit:
                        pygame.draw.line(self.screen, WALL, a, b, 4)
                        pygame.draw.circle(self.screen, WALL, a, 2)
                        pygame.draw.circle(self.screen, WALL, b, 2)
        for gum in game.gums:
            pygame.draw.circle(self.screen, DOT, center(gum),
                               max(2, cell // 12))
        if int(ticks() * 4) % 2:
            for gum in game.super_gums:
                pygame.draw.circle(self.screen, DOT, center(gum), cell // 4)
        radius = cell * 0.42
        player = game.player
        draw_pacman(self.screen, between(player.prev, player.cell,
                                         player.clock / game.player_step()),
                    radius, player.direction)
        for ghost in game.ghosts:
            if ghost.dead_time > 0:
                continue
            pos = between(ghost.prev, ghost.cell,
                          ghost.clock / game.ghost_step(ghost))
            scared = ghost.edible_time > 0
            color = ghost.color
            if scared:
                ending = ghost.edible_time < 2 and int(ticks() * 6) % 2
                color = WHITE if ending else SCARED
            draw_ghost(self.screen, pos, radius, color, ghost.direction,
                       scared)
