# Diagrams

## 1. Screens (states of `App` in `ui.py`)

```mermaid
stateDiagram-v2
    [*] --> menu
    menu --> play: Start Game
    menu --> highscores: Highscores
    menu --> instructions: Instructions
    menu --> quit: Exit
    highscores --> menu: Esc
    instructions --> menu: Esc
    play --> pause: P / Esc
    pause --> play: Resume
    pause --> menu: Main Menu
    play --> name: game over / all levels won
    name --> menu: Enter (score saved)
    quit --> [*]
```

## 2. Game loop (`App.run`)

```mermaid
flowchart TD
    A[clock.tick 60 FPS -> dt] --> B[read keyboard events]
    B --> C{state == play?}
    C -- yes --> D[game.update dt]
    D --> E{game.over?}
    E -- yes --> F[state = name]
    E -- no --> G[draw current screen]
    C -- no --> G
    F --> G
    G --> H{state == quit?}
    H -- no --> A
    H -- yes --> I[pygame.quit]
```

## 3. `Game.update(dt)`

```mermaid
flowchart TD
    A[time_left -= dt] --> B{time_left <= 0?}
    B -- yes --> C[lose a life, restart timer]
    B -- no --> D[move player if step ready]
    D --> E[eat pacgum / super-pacgum]
    E --> F{no pacgums left?}
    F -- yes --> G[next level or victory]
    F -- no --> H[check collisions]
    H --> I[move each ghost if step ready]
    I --> J[check collisions]
```

## 4. Modules

```mermaid
flowchart LR
    main[pac-man.py] --> config[config.py]
    main --> ui[ui.py]
    ui --> game[game.py]
    ui --> highscores[highscores.py]
    game --> maze[maze.py]
    game --> entities[entities.py]
    entities --> maze
    maze --> gen[(mazegenerator package)]
```

## 5. Ghost AI (`Ghost.choose_direction`)

```mermaid
flowchart TD
    A[list open directions] --> B{more than one?}
    B -- yes --> C[remove U-turn]
    B -- no --> D
    C --> D{random < ghost.randomness?}
    D -- yes --> E[random direction]
    D -- no --> F{edible?}
    F -- no --> G[direction closest to player]
    F -- yes --> H[direction farthest from player]
```
