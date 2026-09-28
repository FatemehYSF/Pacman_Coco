"""The player and the ghosts."""
import random

from pacman.maze import DIRS, OPPOSITE, Cell, Maze


class Player:
    """Pac-Man: a cell, a current direction and a wanted direction."""

    def __init__(self, cell: Cell) -> None:
        """Place the player on a cell, not moving."""
        self.cell = cell
        self.prev = cell
        self.direction = 0
        self.wanted = 0
        self.clock = 0.0


class Ghost:
    """A ghost that chases the player, or flees when edible.

    randomness is the chance of a random move: each ghost has its own,
    which gives them different personalities.
    """

    def __init__(self, home: Cell, color: tuple[int, int, int],
                 randomness: float) -> None:
        """Place the ghost in its home corner."""
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
        """Pick the open direction that gets closer to (or away from) target.

        Ghosts do not turn back unless in a dead end, and sometimes pick a
        random direction (see randomness).
        """
        options = [d for d in DIRS if maze.can_move(self.cell, d)]
        back = OPPOSITE.get(self.direction)
        if len(options) > 1 and back in options:
            options.remove(back)
        if not options:
            return 0
        if rng.random() < self.randomness:
            return rng.choice(options)

        def distance(direction: int) -> int:
            x, y = maze.next_cell(self.cell, direction)
            return abs(x - target[0]) + abs(y - target[1])

        if flee:
            return max(options, key=distance)
        return min(options, key=distance)
