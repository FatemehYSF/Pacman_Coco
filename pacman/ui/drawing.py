"""Drawing with pygame shapes: colours, Pac-Man, ghosts and the game board."""
import math

import pygame

from pacman.game import Game
from pacman.maze import CLOSED, DIRS, EAST, NORTH, SOUTH, WEST, Cell

WIDTH, HEIGHT, HUD = 800, 660, 60
Color = tuple[int, int, int]
BLACK, WHITE, GREY = (0, 0, 0), (255, 255, 255), (140, 140, 160)
WALL, BLOCK = (40, 60, 255), (15, 20, 90)
YELLOW, RED, DOT = (255, 225, 0), (255, 70, 70), (255, 184, 151)
SCARED, SCARED_FACE = (40, 40, 220), (255, 184, 151)
ANGLES = {0: 0, EAST: 0, NORTH: 90, WEST: 180, SOUTH: 270}


def ticks() -> float:
    """Seconds since pygame started (used for simple animations)."""
    return float(pygame.time.get_ticks()) / 1000


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


def draw_board(screen: pygame.Surface, game: Game) -> None:
    """Draw the maze, the pacgums, the player and the ghosts."""
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

    for y, row in enumerate(maze.grid):
        for x, walls in enumerate(row):
            x0, y0 = left + x * cell, top + y * cell
            x1, y1 = x0 + cell, y0 + cell
            if walls == CLOSED:
                screen.fill(BLOCK, (x0, y0, cell, cell))
                continue
            for bit, a, b in ((NORTH, (x0, y0), (x1, y0)),
                              (EAST, (x1, y0), (x1, y1)),
                              (SOUTH, (x0, y1), (x1, y1)),
                              (WEST, (x0, y0), (x0, y1))):
                if walls & bit:
                    pygame.draw.line(screen, WALL, a, b, 4)
                    pygame.draw.circle(screen, WALL, a, 2)
                    pygame.draw.circle(screen, WALL, b, 2)
    for gum in game.gums:
        pygame.draw.circle(screen, DOT, center(gum), max(2, cell // 12))
    if int(ticks() * 4) % 2:
        for gum in game.super_gums:
            pygame.draw.circle(screen, DOT, center(gum), cell // 4)
    radius = cell * 0.42
    player = game.player
    draw_pacman(screen, between(player.prev, player.cell,
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
        draw_ghost(screen, pos, radius, color, ghost.direction, scared)
