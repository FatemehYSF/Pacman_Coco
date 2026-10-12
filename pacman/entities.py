"""Pac-Man and the ghosts."""
import random

from pacman.maze import DIRS, OPPOSITE, Cell, Maze


class Player:
    """Pac-Man: where he is and where he is going."""

    def __init__(self, cell: Cell) -> None:
        """Put Pac-Man on a cell, standing still."""
        self.cell = cell
        self.prev = cell
        self.direction = 0
        self.wanted = 0
        self.clock = 0.0


class Ghost:
    """A ghost: chases Pac-Man, runs away when blue, has its own randomness."""

    def __init__(self, home: Cell, color: tuple[int, int, int],
                 randomness: float) -> None:
        """Put the ghost in its corner."""
        self.home = home
        self.cell = home
        self.prev = home
        self.color = color
        self.randomness = randomness
        self.direction = 0
        self.clock = 0.0
        self.edible_time = 0.0
        self.dead_time = 0.0

    def choose_direction(self, maze: Maze, target: Cell, flee: bool,
                         rng: random.Random) -> int:
        """Decide which way the ghost goes next."""
        options = [d for d in DIRS if maze.can_move(self.cell, d)]
        back = OPPOSITE.get(self.direction)
        if len(options) > 1 and back in options:
            options.remove(back)
        if not options:
            return 0
        if rng.random() < self.randomness:
            return rng.choice(options)

        def distance(direction: int) -> int:
            """How far we would be from the target if we went this way."""
            x, y = maze.next_cell(self.cell, direction)
            return abs(x - target[0]) + abs(y - target[1])

        if flee:
            return max(options, key=distance)
        return min(options, key=distance)
