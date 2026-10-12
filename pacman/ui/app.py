"""The app: the window and the main loop."""
from typing import Any

import pygame

from pacman.game import Game
from pacman.highscores import load_scores
from pacman.maze import MazeError
from pacman.ui.drawing import HEIGHT, WIDTH
from pacman.ui.keys import on_key
from pacman.ui.screens import draw_screen


class App:
    """The app: one loop and the screen we are on."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Open the window and load the scores."""
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
        """The main loop: keys, update, draw, until we quit."""
        while self.state != "quit":
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "quit"
                elif event.type == pygame.KEYDOWN:
                    on_key(self, event)
            if self.state == "play" and self.game:
                self.game.update(dt)
                if self.game.over:
                    self.state, self.name = "name", ""
            draw_screen(self)
            pygame.display.flip()
        pygame.quit()

    def start_game(self) -> None:
        """Start a new game, or show an error if the maze fails."""
        try:
            self.game = Game(self.config)
            self.state, self.message = "play", ""
        except MazeError as error:
            self.message = str(error)
            print(f"Error: {error}")
