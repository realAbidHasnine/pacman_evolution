# Pac-Man Evolution

This is a classic Pac-Man game with a twist! In addition to the classic gameplay, this version introduces diagonal movement for Pac-Man, allowing for more fluid and dynamic gameplay.

## Features

*   Classic Pac-Man gameplay: Eat all the pellets to complete a level.
*   Power Pellets: Eat power pellets to gain a temporary speed boost.
*   Diagonal Movement: Pac-Man can move diagonally using the 'q', 'e', 'z', and 'c' keys.
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
*   **`actors.py`**: Defines the `Player` class, which represents Pac-Man. It handles the player's movement, score, and lives.
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

This file defines the actors in the game. Currently, it only defines the `Player` class.

*   **`Actor` class:** A base class for all actors in the game. It is a subclass of `turtle.Turtle`.
*   **`Player` class:** Represents Pac-Man.
    *   `__init__()`: Initializes the player's attributes, such as shape, color, speed, and score.
    *   `queue_direction()`: Queues the next direction for the player to move in.
    *   `move()`: The core of the player's movement logic. It handles both straight and diagonal movements, collision detection, and screen wrapping.
    *   `reset_speed()`: Resets the player's speed to the default value.

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
