# Pac-Man Evolution

This is a classic Pac-Man game with a twist! In addition to the classic gameplay, this version introduces diagonal movement for Pac-Man, allowing for more fluid and dynamic gameplay.

## Features

*   Classic Pac-Man gameplay: Eat all the pellets to complete a level.
*   Power Pellets: Eat power pellets to gain a temporary speed boost.
*   Diagonal Movement: Pac-Man can move diagonally using the 'q', 'e', 'z', and 'c' keys.
*   Diagonal Ghost Chasing: Ghosts can also move and pathfind in 8 directions.
*   Unique Ghost AI: Each ghost has its own chase style, making the enemies behave differently.
*   Score and Lives: Keep track of your score and remaining lives.
*   Screen Wrapping: The screen wraps around, allowing Pac-Man to move from one side to the other.

## How to Play

1.  **Run the game:**
    ```bash
    python main.py
    ```

2.  **Controls:**
    *   **Up:** Up Arrow
    *   **Down:** Down Arrow
    *   **Left:** Left Arrow
    *   **Right:** Right Arrow
    *   **Up-Left:** q
    *   **Up-Right:** e
    *   **Down-Left:** z
    *   **Down-Right:** c

## Project Structure

The project is structured into the following files:

*   **`main.py`**: The main entry point of the game. It initializes the game, handles the game loop, and binds the controls.
*   **`actors.py`**: Defines Pac-Man, the shared ghost movement system, and the unique ghost AI classes.
*   **`mazes.py`**: Contains the maze layout and the `Maze` class, which is used to interact with the maze.
*   **`renderer.py`**: Responsible for drawing the game elements, including the maze, pellets, and UI.
*   **`constants.py`**: Contains all the constants used in the game, such as screen dimensions, player speed, and maze layout details.

## Code Overview

### `main.py`

This file is the starting point of the game.

*   `init_screen()`: Initializes the main game screen using the `turtle` module.
*   `bind_controls()`: Binds the keyboard controls to the player's movement. It handles both orthogonal and diagonal movements.
*   `game_loop()`: The main game loop. It updates the game state, handles pellet and power pellet collection, and redraws the screen.
*   `main()`: The main function that initializes the game objects and starts the game loop.

### `actors.py`

This file defines the moving actors in the game: Pac-Man and the four ghosts. It also contains shared helper functions for grid movement, diagonal movement, pathfinding, and ghost target selection.

*   **`Actor` class:** A base class for all actors in the game. It is a subclass of `turtle.Turtle`.
*   **`Player` class:** Represents Pac-Man.
    *   `__init__()`: Initializes the player's attributes, such as shape, color, speed, and score.
    *   `queue_direction()`: Queues the next direction for the player to move in.
    *   `move()`: The core of the player's movement logic. It handles straight movement, diagonal movement, buffered turns, collision detection, and screen wrapping.
    *   `reset_speed()`: Resets the player's speed to the default value.

## Movement and Ghost AI

### Shared Movement Helpers

The movement system uses both world coordinates and grid coordinates.

*   **World coordinates:** Turtle screen positions, such as `xcor()` and `ycor()`. These are used to draw actors on the screen.
*   **Grid coordinates:** Maze cell positions, such as `(gx, gy)`. These are used for wall checks, ghost decisions, and pathfinding.

Important helper ideas:

*   `DIRECTION_VECTORS`: Converts direction names like `"up-right"` into grid movement such as `(1, -1)`.
*   `EIGHT_WAY_STEPS`: Allows movement in 8 directions: up, down, left, right, and the 4 diagonals.
*   `wrap_cell()`: Wraps a grid coordinate around the maze edges.
*   `is_open_cell()`: Checks whether a grid cell is not a wall.
*   `can_step_grid()`: Checks whether a move is legal. For diagonal movement, it also prevents cutting through two wall corners.
*   `octile_distance()`: Measures distance in an 8-direction grid. It is useful when diagonal movement is allowed.
*   `bfs()`: Finds a path through the maze using 8-direction movement.

### Pac-Man Movement

Pac-Man keeps a `direction` and a `buffered_direction`.

*   `direction` is the direction Pac-Man is currently moving.
*   `buffered_direction` stores the player's next requested turn for a short time.
*   Pac-Man can move straight or diagonally.
*   Diagonal speed is scaled by `0.707` so diagonal movement is not faster than straight movement.
*   Before accepting a buffered turn, Pac-Man checks whether the requested direction is legal from the current maze cell.
*   Collision detection uses a smaller hitbox than the full cell size, which makes movement feel less sticky near walls.

### BaseGhost

`BaseGhost` contains the shared movement and decision framework used by every ghost.

Each ghost stores:

*   `gx`, `gy`: The ghost's current grid cell.
*   `next_gx`, `next_gy`: The next grid cell the ghost wants to reach.
*   `target_x`, `target_y`: The world coordinate of the next target cell.
*   `prev_gx`, `prev_gy`: The previous grid cell, used to avoid unnecessary 180-degree turns.

How `BaseGhost.move()` works:

1.  It calculates game progress using the number of pellets eaten.
2.  It increases ghost speed as more pellets are eaten.
3.  It moves the ghost toward the current target cell.
4.  When the ghost reaches that target cell, it updates its grid position.
5.  It asks the specific ghost class to choose the next cell.
6.  It moves toward that next cell smoothly in world coordinates.

How `BaseGhost.get_neighbors()` works:

*   It checks all 8 possible movement directions.
*   It allows diagonal movement only when the destination is open.
*   It blocks diagonal movement through tight wall corners.

How `BaseGhost.choose_next_target()` works:

*   It gets all valid neighboring cells.
*   It avoids reversing into the previous cell when other choices exist.
*   It calls the individual ghost's `get_best_neighbor()` method.
*   This is where each ghost's unique AI behavior is applied.

### Red Ghost: Pressure Hunter

The red ghost is designed to feel aggressive but slightly unpredictable.

Logic:

*   It looks at Pac-Man's current grid cell.
*   It ranks all valid neighboring cells by which one gets closest to Pac-Man.
*   Most of the time, it picks the closest option.
*   Sometimes, it picks the second-best or another nearby option.

Why this is unique:

*   Red does not use full BFS pathfinding.
*   It makes short-term greedy decisions.
*   The small randomness prevents it from feeling robotic.

How to explain it:

> Red is a pressure ghost. It usually moves directly toward Pac-Man using local distance, but it sometimes varies its route so the chase is less predictable.

### Yellow Ghost: Direct Pathfinder

The yellow ghost is the pure chase ghost.

Logic:

*   It converts Pac-Man's world position into a grid cell.
*   It uses BFS to find an 8-direction path to Pac-Man's current cell.
*   It chooses the first step of that path.
*   If BFS cannot find a path, it falls back to the closest valid neighboring cell.

Why this is unique:

*   Yellow is the most direct and logical chaser.
*   It uses actual pathfinding instead of only local distance.
*   It represents a classic search-based AI.

How to explain it:

> Yellow uses BFS to find the shortest available path to Pac-Man's current grid position, including diagonal movement.

### Green Ghost: Ambush Predictor

The green ghost tries to predict where Pac-Man is going instead of chasing where Pac-Man is now.

Logic:

*   It reads Pac-Man's current direction.
*   It targets 4 cells ahead of Pac-Man in that direction.
*   If Pac-Man is moving diagonally, the target is also diagonal.
*   It uses BFS to pathfind toward that predicted future cell.
*   If Pac-Man is stopped, Green falls back to chasing Pac-Man's current cell.

Why this is unique:

*   Green is predictive.
*   It does not chase Pac-Man directly.
*   It tries to intercept Pac-Man by aiming ahead.

How to explain it:

> Green is an ambush ghost. It predicts Pac-Man's future position by looking 4 cells ahead in Pac-Man's current movement direction, then pathfinds toward that predicted cell.

### Blue Ghost: Flanker and Scatter Ghost

The blue ghost has two modes: scatter and chase.

Scatter mode:

*   Blue targets a fixed corner of the maze.
*   This creates breathing room and makes its behavior different from constant chasing.

Chase mode:

*   Blue reads Pac-Man's current direction.
*   Instead of targeting Pac-Man directly, it calculates side positions relative to Pac-Man's movement.
*   It chooses a flank target and pathfinds toward that side position.
*   If Pac-Man is stopped, Blue falls back to targeting Pac-Man directly.

Why this is unique:

*   Blue is not a direct chaser.
*   It tries to approach from the side.
*   Its scatter/chase timer gives it changing behavior over time.

How to explain it:

> Blue is a flanking ghost. It alternates between scatter mode and chase mode. In chase mode, it targets a side position relative to Pac-Man's direction so it can pressure Pac-Man from an angle instead of following directly.

### `mazes.py`

This file defines the maze layout and provides a `Maze` class to interact with it.

*   `maze_level_1`: A list of strings that represents the maze layout. 'X' is a wall, '.' is a pellet, and 'O' is a power pellet.
*   **`Maze` class:**
    *   `__init__()`: Initializes the maze by parsing the `maze_level_1` data.
    *   `_calculate_maze_data()`: A helper function to parse the maze data and store the positions of walls, pellets, and power pellets.
    *   `is_wall()`: Checks if a given coordinate is a wall.
*   `get_maze()`: A factory function that returns a `Maze` object.

### `renderer.py`

This file is responsible for drawing the game elements.

*   **`Pen` class:** A base class for all the drawing pens. It is a subclass of `turtle.Turtle`.
*   **`Wall` class:** Draws the walls of the maze.
*   **`Pellet` class:** Draws the pellets in the maze.
*   **`PowerPellet` class:** Draws the power pellets in the maze.
*   **`UiPanel` class:** Draws the UI panel, including the score and lives.

### `constants.py`

This file contains all the constants used in the game. This makes it easy to configure the game's parameters, such as screen size, player speed, and maze dimensions.
