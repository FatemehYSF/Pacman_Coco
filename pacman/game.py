"""Game rules: levels, score, lives, eating, collisions and cheats."""
import random
from typing import Any

from pacman.entities import Ghost, Player
from pacman.maze import Maze, MazeError

PLAYER_STEP = 0.15
GHOST_STEP = 0.35
GHOSTS = [((255, 0, 0), 0.1), ((255, 184, 255), 0.25),
          ((0, 255, 255), 0.4), ((255, 184, 82), 0.6)]


class Game:
    """The state of one game, from level 1 until win or game over."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Start a new game at level 1. May raise MazeError."""
        self.config = config
        self.level = 0
        self.score = 0
        self.lives: int = config["lives"]
        self.over = False
        self.won = False
        self.cheat = False
        self.invincible = False
        self.frozen = False
        self.fast = False
        self.start_level()

    def start_level(self) -> None:
        """Build the maze, pacgums, player and ghosts of the current level."""
        size = self.config["levels"][self.level]
        seed = self.config["seed"] if self.level == 0 else 0
        self.maze = Maze(size["width"], size["height"], seed)
        self.rng = random.Random(seed or None)
        self.time_left = float(self.config["level_max_time"])
        self.super_gums = set(self.maze.corners) - {self.maze.center}
        cells = [c for c in self.maze.open_cells()
                 if c != self.maze.center and c not in self.super_gums]
        count = min(len(cells), self.config["pacgum"])
        self.gums = set(self.rng.sample(cells, count))
        self.player = Player(self.maze.center)
        self.ghosts = [Ghost(corner, color, randomness) for corner,
                       (color, randomness) in zip(self.maze.corners, GHOSTS)]

    def next_level(self) -> None:
        """Go to the next level, or win the game after the last one."""
        self.level += 1
        if self.level >= len(self.config["levels"]):
            self.level -= 1
            self.won = self.over = True
            return
        try:
            self.start_level()
        except MazeError as error:
            print(f"Error: {error}")
            self.over = True

    def lose_life(self) -> None:
        """Remove a life and send everybody back to their start cell."""
        if self.over:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.over = True
            return
        self.player = Player(self.maze.center)
        for ghost in self.ghosts:
            ghost.cell = ghost.prev = ghost.home
            ghost.direction = 0

    def player_step(self) -> float:
        """Seconds the player needs to move one cell."""
        return PLAYER_STEP / 2 if self.fast else PLAYER_STEP

    def ghost_step(self, ghost: Ghost) -> float:
        """Seconds a ghost needs to move one cell (slower when edible)."""
        return GHOST_STEP * 2 if ghost.edible_time > 0 else GHOST_STEP

    def toggle_cheat(self) -> None:
        """Turn cheat mode on or off (off also disables every cheat)."""
        self.cheat = not self.cheat
        if not self.cheat:
            self.invincible = self.frozen = self.fast = False

    def update(self, dt: float) -> None:
        """Advance the game by dt seconds."""
        self.time_left -= dt
        if self.time_left <= 0:
            self.lose_life()
            self.time_left = float(self.config["level_max_time"])
            return
        self.move_player(dt)
        self.move_ghosts(dt)

    def move_player(self, dt: float) -> None:
        """Move the player one cell when its step timer is ready."""
        player = self.player
        player.clock += dt
        if player.clock < self.player_step():
            return
        player.clock = 0.0
        player.prev = player.cell
        if player.wanted and self.maze.can_move(player.cell, player.wanted):
            player.direction = player.wanted
        if player.direction and self.maze.can_move(player.cell,
                                                   player.direction):
            player.cell = self.maze.next_cell(player.cell, player.direction)
        self.eat()
        self.check_collisions()

    def move_ghosts(self, dt: float) -> None:
        """Move every ghost one cell when its own step timer is ready."""
        for ghost in self.ghosts:
            if ghost.dead_time > 0:
                ghost.dead_time -= dt
                continue
            ghost.edible_time = max(0.0, ghost.edible_time - dt)
            if self.frozen:
                ghost.prev = ghost.cell
                continue
            ghost.clock += dt
            if ghost.clock < self.ghost_step(ghost):
                continue
            ghost.clock = 0.0
            ghost.prev = ghost.cell
            ghost.direction = ghost.choose_direction(
                self.maze, self.player.cell, ghost.edible_time > 0, self.rng)
            if ghost.direction:
                ghost.cell = self.maze.next_cell(ghost.cell, ghost.direction)
            self.check_collisions()

    def eat(self) -> None:
        """Eat the pacgum under the player; win the level if none are left."""
        cell = self.player.cell
        if cell in self.gums:
            self.gums.remove(cell)
            self.score += self.config["points_per_pacgum"]
        elif cell in self.super_gums:
            self.super_gums.remove(cell)
            self.score += self.config["points_per_super_pacgum"]
            for ghost in self.ghosts:
                if ghost.dead_time <= 0:
                    ghost.edible_time = self.config["frightened_duration"]
        if not self.gums and not self.super_gums:
            self.next_level()

    def check_collisions(self) -> None:
        """Handle a ghost and the player being on the same cell."""
        for ghost in self.ghosts:
            if ghost.dead_time > 0 or ghost.cell != self.player.cell:
                continue
            if ghost.edible_time > 0:
                self.score += self.config["points_per_ghost"]
                ghost.cell = ghost.prev = ghost.home
                ghost.direction = 0
                ghost.edible_time = 0.0
                ghost.dead_time = self.config["ghost_respawn_time"]
            elif not self.invincible:
                self.lose_life()
                return
