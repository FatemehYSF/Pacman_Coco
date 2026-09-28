"""Turn the external A-Maze-ing generator output into a playable grid."""
import sys

from mazegenerator import MazeGenerator

Cell = tuple[int, int]
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
DIRS: dict[int, Cell] = {NORTH: (0, -1), EAST: (1, 0),
                         SOUTH: (0, 1), WEST: (-1, 0)}
OPPOSITE: dict[int, int] = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST,
                            WEST: EAST}
CLOSED = 15


class MazeError(Exception):
    """Raised when the maze generator fails."""


class Maze:
    """A grid of cells; each cell stores its walls as bits (N=1 E=2 S=4 W=8).

    A cell with all 4 walls (15) is a solid block (the '42' pattern).
    """

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Generate a maze with the external package (PERFECT = False)."""
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))
        try:
            generator = MazeGenerator(size=(width, height), perfect=False,
                                      seed=seed)
            self.grid: list[list[int]] = [list(row) for row in generator.maze]
        except Exception as error:
            raise MazeError(f"maze generator failed: {error}") from error
        if len(self.grid) != height or any(len(r) != width
                                           for r in self.grid):
            raise MazeError("maze generator returned a wrong-sized grid")
        self.width = width
        self.height = height
        self.center = self.nearest_open((width // 2, height // 2))
        self.corners = [self.nearest_open(c) for c in
                        ((0, 0), (width - 1, 0),
                         (0, height - 1), (width - 1, height - 1))]

    def is_open(self, cell: Cell) -> bool:
        """Return True if cell is inside the maze and not a solid block."""
        x, y = cell
        return (0 <= x < self.width and 0 <= y < self.height
                and self.grid[y][x] != CLOSED)

    def next_cell(self, cell: Cell, direction: int) -> Cell:
        """Return the neighbour of cell in the given direction."""
        dx, dy = DIRS[direction]
        return cell[0] + dx, cell[1] + dy

    def can_move(self, cell: Cell, direction: int) -> bool:
        """Return True if no wall blocks moving from cell in direction."""
        target = self.next_cell(cell, direction)
        if not self.is_open(cell) or not self.is_open(target):
            return False
        return not (self.grid[cell[1]][cell[0]] & direction
                    or self.grid[target[1]][target[0]] & OPPOSITE[direction])

    def open_cells(self) -> list[Cell]:
        """Return every walkable cell."""
        return [(x, y) for y in range(self.height) for x in range(self.width)
                if self.grid[y][x] != CLOSED]

    def nearest_open(self, target: Cell) -> Cell:
        """Return the walkable cell closest to target."""
        return min(self.open_cells(), key=lambda c: abs(c[0] - target[0])
                   + abs(c[1] - target[1]))
