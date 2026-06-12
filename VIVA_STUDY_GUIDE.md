# Viva Study Guide: Pac-Man Evolution

This guide provides a comprehensive analysis of the "Pac-Man Evolution" Python project, designed to prepare a student for a university viva.

---

## **I. Per-File Analysis**

### **`main.py`**

*   **Single Responsibility:** Orchestrates the entire game flow, including initialization, the main game loop, UI management, and handling game state transitions (start, win, lose, restart).

*   **Functions & Methods:**

    *   `init_screen()`
        *   **Parameters:** None
        *   **What it does:** Sets up the main Turtle graphics window, configuring its size, title, background color, and disabling automatic screen updates (`tracer(0)`) to allow for manual frame rendering.
        *   **Calls:** `turtle.Screen()`, `screen.tracer()`, `screen.title()`, `screen.setup()`, `screen.bgcolor()`
        *   **Called By:** `main()`

    *   `bind_controls(screen, player)`
        *   **Parameters:** `screen` (turtle.Screen object), `player` (Player object)
        *   **What it does:** Configures all keyboard input. It uses `onkeypress` and `onkeyrelease` with a `set` of `pressed_keys` to handle 8-directional movement when arrow keys are held down simultaneously. It also binds single-press keys (q, e, z, c) for direct diagonal movement.
        *   **Calls:** `player.queue_direction()`, `screen.listen()`, `screen.onkeypress()`, `screen.onkeyrelease()`
        *   **Called By:** `start_new_game()`
        *   **Non-obvious Logic:** The `update_direction` inner function is the core of the 8-way arrow key movement. It checks for specific combinations of keys within the `pressed_keys` set to determine the final direction, prioritizing diagonal movements.

    *   `show_game_over(screen, ui_panel, restart_callback)`
        *   **Parameters:** `screen` (turtle.Screen), `ui_panel` (UiPanel), `restart_callback` (function)
        *   **What it does:** Halts the game and displays a "GAME OVER" message. It then draws a clickable "RESTART" button and sets up a screen click handler that will execute the `restart_callback` if the click occurs within the button's boundaries.
        *   **Calls:** `ui_panel.write()`, multiple `ui_panel` drawing methods for the button, `screen.onclick()`, `screen.update()`
        *   **Called By:** `game_loop()`

    *   `show_victory(screen, ui_panel, restart_callback)`
        *   **Parameters:** `screen`, `ui_panel`, `restart_callback`
        *   **What it does:** Halts the game and displays a "YOU WIN!" message. It functions identically to `show_game_over` by drawing a restart button and waiting for a click.
        *   **Calls:** `ui_panel.write()`, drawing methods, `screen.onclick()`, `screen.update()`
        *   **Called By:** `game_loop()`

    *   `reset_positions(player, ghosts, player_start_x, player_start_y)`
        *   **Parameters:** `player` (Player), `ghosts` (list), `player_start_x` (float), `player_start_y` (float)
        *   **What it does:** Resets the player and all ghosts to their starting positions. It stops the player's movement, clears their buffered direction, and resets each ghost's grid and world coordinates, effectively preparing for a new round.
        *   **Calls:** `player.goto()`, `ghost.grid_to_world()`, `ghost.goto()`
        *   **Called By:** `game_loop()`, `start_new_game()`

    *   `game_loop(...)`
        *   **Parameters:** `screen`, `player`, `ghosts`, `score_panel`, `lives_panel`, `ui_panel`, `pellet_pen`, `power_pellet_pen`, `player_start_x`, `player_start_y`, `total_pellets`, `restart_callback`
        *   **What it does:** This is the heart of the game, executed approximately 60 times per second via `screen.ontimer`. It checks for pellet/power pellet collisions, updates the score, moves the player and ghosts, checks for ghost-player collisions, and handles the consequences (decrementing lives or ending the game).
        *   **Calls:** `score_panel.write_score()`, `lives_panel.write_lives()`, `show_victory()`, `player.distance()`, `pellet_pen.clearstamp()`, `player.reset_speed()`, `screen.ontimer()` (recursive call), `player.move()`, `ghost.move()`, `reset_positions()`, `show_game_over()`, `screen.update()`
        *   **Non-obvious Logic:** Pellet collection iterates over a `list` copy of `pellet_pen.stamps.items()`. This is a critical pattern that prevents a `RuntimeError` by allowing safe deletion from the dictionary during iteration.

    *   `main()`
        *   **Parameters:** None
        *   **What it does:** The main entry point. It initializes the screen and all game objects (maze, renderers, player, ghosts). It defines the `start_new_game` closure, which contains the logic for a full game reset, and then calls it to begin the first game.
        *   **Calls:** `init_screen()`, `get_maze()`, `Wall()`, `Pellet()`, `PowerPellet()`, `UiPanel()`, `Player()`, `RedGhost()`, `YellowGhost()`, `GreenGhost()`, `BlueGhost()`, `start_new_game()`, `screen.mainloop()`
        *   **Called By:** `if __name__ == "__main__"` block.

---

### **`actors.py`**

*   **Single Responsibility:** Defines the behaviors, movement logic, and AI for all dynamic entities in the game (the Player and the Ghosts).

*   **Functions & Methods:**

    *   `wrap_cell(gx, gy, grid)`
        *   **Parameters:** `gx` (int), `gy` (int), `grid` (list of lists)
        *   **What it does:** Implements the screen-wrapping tunnel effect at the grid level. It takes potentially out-of-bounds grid coordinates and maps them to valid coordinates on the opposite side of the maze using the modulo operator.
        *   **Calls:** None
        *   **Called By:** `is_open_cell`, several pathfinding functions (`bfs`, `dfs`, etc.), `BaseGhost.minimax_neighbor_to`.

    *   `is_open_cell(gx, gy, grid)`
        *   **Parameters:** `gx`, `gy`, `grid`
        *   **What it does:** Checks if a specific grid cell is traversable (i.e., not a wall, represented by "X"). It correctly handles checks for coordinates that are off-screen by using `wrap_cell`.
        *   **Calls:** `wrap_cell()`
        *   **Called By:** `can_step_grid()`, `get_closest_valid_cell()`

    *   `can_step_grid(gx, gy, dx, dy, grid)`
        *   **Parameters:** `gx`, `gy` (start coords), `dx`, `dy` (move delta), `grid`
        *   **What it does:** Determines if a move is legal. For diagonal moves, it enforces a crucial rule: the move is only allowed if both adjacent cardinal cells are also open, preventing actors from "squeezing" through diagonal wall corners.
        *   **Calls:** `is_open_cell()`
        *   **Called By:** `Player.move()`, all pathfinding functions, `BaseGhost.get_neighbors()`.

    *   `octile_distance(a, b)`
        *   **Parameters:** `a` (tuple), `b` (tuple)
        *   **What it does:** Calculates the octile distance, a heuristic for 8-directional movement. It's the maximum of the absolute differences in the x and y coordinates, representing the minimum number of steps needed to get from `a` to `b`.
        *   **Calls:** None
        *   **Called By:** `BaseGhost.closest_neighbor_to()`, `BaseGhost.minimax_neighbor_to()`, `BlueGhost.get_best_neighbor()`.

    *   `direction_to_delta(direction)`
        *   **Parameters:** `direction` (str)
        *   **What it does:** Translates a human-readable direction string (e.g., "up-left") into a grid coordinate delta (e.g., `(-1, -1)`).
        *   **Calls:** `DIRECTION_VECTORS.get()`
        *   **Called By:** `Player.move()`, `BlueGhost.get_best_neighbor()`.

    *   `bfs(start, target, grid)`
        *   **What it does:** Implements Breadth-First Search to find the absolute shortest path on the grid. It explores the grid layer by layer, guaranteeing an optimal path in terms of number of steps.
        *   **Calls:** `wrap_cell`, `collections.deque`, `can_step_grid`
        *   **Called By:** `BaseGhost.path_neighbor_to()` (used by Red Ghost).

    *   `dfs(start, target, grid)`
        *   **What it does:** Implements Depth-First Search. It explores as far as possible down one path before backtracking. This finds *a* path, but it is not guaranteed to be the shortest, leading to more unpredictable movement.
        *   **Calls:** `wrap_cell`, `can_step_grid`
        *   **Called By:** `BaseGhost.dfs_neighbor_to()` (used by Yellow Ghost).

    *   `ucs(start, target, grid)`
        *   **What it does:** Implements Uniform Cost Search. It's similar to BFS but uses a priority queue and accounts for different step costs (diagonal moves cost `1.414`, cardinal `1.0`), finding the path with the lowest total travel distance.
        *   **Calls:** `wrap_cell`, `heapq`, `step_cost`, `can_step_grid`
        *   **Called By:** `BaseGhost.ucs_neighbor_to()` (used by Blue Ghost).

    *   `get_closest_valid_cell(target, grid)`
        *   **What it does:** A failsafe function. If a target cell is inside a wall, it performs a BFS outward from that point to find the nearest accessible cell. This prevents ghosts from getting stuck trying to path into an invalid location.
        *   **Calls:** `wrap_cell`, `is_open_cell`, `collections.deque`
        *   **Called By:** All `neighbor_to` methods in `BaseGhost`.

    *   **Class `Player(Actor)`**
        *   `queue_direction(self, direction)`: Implements input buffering. It stores the player's last directional input for `BUFFER_FRAMES` (12 frames), allowing the player to press a turn key slightly before reaching an intersection.
        *   `move(self)`: Contains the complete player movement logic. It checks if a buffered turn can be executed (only when near a cell center), calculates the next pixel position (normalizing diagonal speed), performs pixel-based collision detection against walls, and handles screen wrapping.

    *   **Class `BaseGhost(Actor)`**
        *   `grid_to_world`/`world_to_grid`: Helper functions for converting between the discrete maze grid and the continuous pixel-based world coordinates.
        *   `choose_next_target(...)`: The core AI decision point. It gets all valid neighboring cells, filters out the one that would cause a 180-degree turn (a standard Pac-Man rule), and then delegates the final choice to `get_best_neighbor`, which is unique to each ghost subclass.
        *   `path_neighbor_to`/`dfs_neighbor_to`/`ucs_neighbor_to`: Wrapper methods that execute a full pathfinding algorithm (`bfs`, `dfs`, `ucs`) and return the neighbor that is the first step on the resulting path. This connects high-level pathfinding to low-level movement.
        *   `minimax_neighbor_to(...)`: A more advanced AI logic that simulates a few moves ahead. It models the game as a turn-based struggle between the ghost (maximizer, trying to get closer) and a simulated Pac-Man (minimizer, trying to get further away), then chooses the move with the best outcome.
        *   `move(...)`: The ghost's update loop. It implements the "evolution" by increasing its speed and size based on the percentage of pellets eaten. It moves smoothly towards its current target cell, and once it arrives, it calls `choose_next_target` to get a new destination.

    *   **Ghost Subclasses (`RedGhost`, `YellowGhost`, `GreenGhost`, `BlueGhost`)**
        *   Each subclass's unique behavior is defined by its implementation of `get_best_neighbor`.
        *   **`RedGhost`:** Uses `path_neighbor_to` (BFS), making it a relentless chaser that always takes the shortest path.
        *   **`YellowGhost`:** Uses `dfs_neighbor_to` (DFS), making its movement seem random and unpredictable as it follows non-optimal paths.
        *   **`GreenGhost`:** Uses `minimax_neighbor_to`, making it an "ambusher" that tries to cut Pac-Man off by predicting his movement.
        *   **`BlueGhost`:** Implements a state machine. In `chase` mode, it's a "flanker," targeting a point to the side of Pac-Man. In `scatter` mode, it targets a fixed corner of the maze. The duration of its `scatter` mode decreases as the game progresses.

---

### **`constants.py`**

*   **Single Responsibility:** Centralizes all configurable "magic numbers" and constants used throughout the project, making gameplay tuning easy and the code more readable.

*   **Constants:** (Detailed in Section VIII)

---

### **`mazes.py`**

*   **Single Responsibility:** Stores the maze layout data as a list of strings and provides a `Maze` class to parse this data and handle spatial queries (like wall collision checks).

*   **Functions & Methods:**

    *   **Class `Maze`**
        *   `__init__(self, maze_level)`: The constructor takes the raw maze layout and immediately calls `_calculate_maze_data` to process it.
        *   `_calculate_maze_data(self)`: This is the parser. It iterates through every character of the grid, converting grid coordinates to world (pixel) coordinates and populating lists of `walls`, `pellets`, and `power_pellets`.
        *   `is_wall(self, x, y)`: The primary collision detection function. It takes pixel coordinates, converts them back to grid coordinates, and checks if that character in the original `grid` is an "X".

    *   `get_maze(level)`
        *   **Parameters:** `level` (list of strings)
        *   **What it does:** A simple factory function that instantiates and returns a `Maze` object from a given level layout.
        *   **Calls:** `Maze()`
        *   **Called By:** `main()`

---

### **`renderer.py`**

*   **Single Responsibility:** Contains all classes and logic related to drawing game elements onto the screen using the `turtle` library.

*   **Classes:**

    *   **`Pen(turtle.Turtle)`**: A generic base class for all other renderers. It sets common turtle properties like hiding the turtle, lifting the pen, and setting drawing speed to maximum.

    *   **`Wall(Pen)`**: Responsible for drawing the maze walls. Its `draw()` method iterates through the `maze.walls` list and uses `self.stamp()` to efficiently draw a blue square at each wall coordinate.

    *   **`Pellet(Pen)`** & **`PowerPellet(Pen)`**: Responsible for drawing pellets. Their `draw()` methods iterate through the maze's pellet lists and stamp a shape at each coordinate.
        *   **Non-obvious Logic:** They store the returned `stamp_id` from each `stamp()` call in a dictionary (`self.stamps`), mapping world coordinates to the ID. This is essential for `main.py` to be able to find and delete the correct stamp when a pellet is eaten.

    *   **`UiPanel(Pen)`**: A multi-purpose class for drawing the entire non-game UI.
        *   `draw_ui_area()`: Draws the rectangular border on the right side of the screen.
        *   `draw_title_and_legend()`: Writes the game title and the helpful legend that explains each ghost's AI strategy.
        *   `write_score(score)` / `write_lives(lives)`: Methods to display the current score and lives, clearing their previous text before writing the new values.

---
## **II. Ghost AI — Deep Dive**

This section details the specific AI and behavior of each of the four ghosts.

### **Red Ghost (`RedGhost`)**

*   **Name/Identifier:** `red_ghost`, color "red".
*   **Targeting Logic:** The Red Ghost is a pure chaser. Its target is always Pac-Man's exact current grid cell `(pgx, pgy)`.
*   **State Machine:** It has no explicit state machine; it is always in "chase" mode.
*   **Speed/Size Change:** Its speed starts at `base_speed = 2.0` and increases linearly up to `2.0 + 2.7 = 4.7` as pellets are eaten. Its size scales from `0.9` to `0.9 + 0.3 = 1.2`.
*   **Direction Algorithm:**
    1.  At an intersection, it gets a list of all valid neighboring cells.
    2.  It filters out the cell it just came from to prevent 180-degree turns.
    3.  It calls `path_neighbor_to`, which executes a Breadth-First Search (BFS) to find the absolute shortest path to Pac-Man's cell.
    4.  It chooses the neighbor that is the first step on this optimal path.
*   **Frightened Mode:** This codebase does not implement a frightened mode. The ghosts are always aggressive.

### **Yellow Ghost (`YellowGhost`)**

*   **Name/Identifier:** `yellow_ghost`, color "orange".
*   **Targeting Logic:** Like the Red Ghost, its target is always Pac-Man's exact grid cell. The difference is in *how* it paths to that target.
*   **State Machine:** No explicit state machine. Always in "chase" mode.
*   **Speed/Size Change:** Its speed starts at `base_speed = 2.2` and increases to `4.9`. Its size scales identically to the Red Ghost.
*   **Direction Algorithm:**
    1.  Gets valid neighbors, preventing 180-degree turns.
    2.  It calls `dfs_neighbor_to`, which executes a Depth-First Search (DFS) to find a path to Pac-Man.
    3.  Because DFS explores one path to its conclusion before backtracking, the resulting path is often long and illogical. This makes the Yellow Ghost's movement seem erratic and unpredictable, even though it's still deterministic.
*   **Frightened Mode:** Not implemented.

### **Green Ghost (`GreenGhost`)**

*   **Name/Identifier:** `green_ghost`, color "medium spring green".
*   **Targeting Logic:** Its target is Pac-Man's cell, but its decision-making is more sophisticated, aiming to intercept rather than just chase.
*   **State Machine:** No explicit state machine.
*   **Speed/Size Change:** Its speed starts at `base_speed = 2.1` and increases to `4.8`. Its size scales identically to the others.
*   **Direction Algorithm:**
    1.  Gets valid neighbors, preventing 180-degree turns.
    2.  It calls `minimax_neighbor_to` with a depth of 3. This function simulates a 3-move game:
        *   **Ghost's turn (MAX):** It considers moving to each neighbor.
        *   **Pac-Man's turn (MIN):** For each possible ghost move, it simulates where Pac-Man might move to escape.
        *   **Evaluation:** The "score" of a board state is based on minimizing the distance to Pac-Man and also penalizing states where Pac-Man has many escape routes.
    3.  It chooses the neighbor that leads to the highest score (most advantageous position) after this 3-move lookahead. This makes it appear to be "smarter" and capable of ambushing the player.
*   **Frightened Mode:** Not implemented.

### **Blue Ghost (`BlueGhost`)**

*   **Name/Identifier:** `blue_ghost`, color "cyan".
*   **Targeting Logic:** This is the most complex ghost, with two distinct targeting modes.
    *   **Chase Mode:** It acts as a "flanker." It calculates two target cells, one 4 cells to the left of Pac-Man's current position (perpendicular to his direction) and one 4 cells to the right. It then chooses to target the flank that is currently farther away from its own position, attempting to pincer Pac-Man.
    *   **Scatter Mode:** It ignores Pac-Man completely and targets a fixed grid cell in the bottom-right of the maze: `(cols - 2, rows - 2)`.
*   **State Machine:** It uses a time-based state machine controlled by `update_mode`.
    1.  Starts in `scatter` mode. The duration is `max(1.0, 7.0 - fraction_eaten * 6.0)`, so it starts at 7 seconds and decreases to 1 second as the maze is cleared.
    2.  When the scatter timer expires, it switches to `chase` mode for a fixed 20 seconds.
    3.  When the chase timer expires, it switches back to `scatter`, and the cycle repeats.
*   **Speed/Size Change:** Its speed starts at `base_speed = 2.3` and increases to `5.0`. Its size scales identically.
*   **Direction Algorithm:**
    1.  Gets valid neighbors, preventing 180-degree turns.
    2.  Determines its target cell based on its current `mode` (scatter corner or flank position).
    3.  It calls `ucs_neighbor_to`, which uses Uniform Cost Search (UCS) to find the most distance-efficient path to its target, accounting for the higher cost of diagonal moves.
*   **Frightened Mode:** Not implemented.

---
## **III. Maze System**

*   **Data Structure:** The maze is fundamentally represented as a `list` of `str`ings (`maze_level_1` in `mazes.py`). Each string is a row, and each character is a cell. This is stored in `Maze.grid`.

*   **Cell Value Meanings:**
    *   `'X'`: A wall. Impassable.
    *   `'.'` : A regular pellet. Worth 10 points.
    *   `'O'`: A power pellet. Worth 50 points and grants a temporary speed boost.

*   **Coordinate Conversion (Pixel to Grid):** The formula is in `Maze.is_wall` and `BaseGhost.world_to_grid`:
    *   `grid_x = int((x - MAZE_LEVEL_START_X + CELL_SIZE // 2) / CELL_SIZE)`
    *   `grid_y = int((MAZE_LEVEL_START_Y - y + CELL_SIZE // 2) / CELL_SIZE)`
    *   **Explanation:** It takes the world coordinate (`x` or `y`), offsets it by the maze's top-left starting corner, adds half a cell size to center the coordinate within the grid cell, and then divides by the cell size to get the integer grid index. The Y-axis is inverted because turtle coordinates have (0,0) at the center with Y increasing upwards, while the grid index has (0,0) at the top-left with Y increasing downwards.

*   **Wall Collision:**
    *   **For Ghosts:** Collision is grid-based and proactive. Before moving, they check if a target cell is valid using `can_step_grid`. They never move into a wall.
    *   **For Pac-Man:** Collision is pixel-based and reactive, handled in `Player.move`. Before moving, it calculates the `next_x` and `next_y`. It then checks if the leading edges of the player's hitbox will be inside a wall at that new position by calling `self.maze.is_wall()`. If a move in one axis is blocked but the other is not (e.g., trying to move up-right but hitting a wall above), the `final_x` will be updated but the `final_y` will not, resulting in a "slide" along the wall.

*   **Pellet Removal:**
    *   In `game_loop`, the code iterates through a list of all active pellet stamps.
    *   It checks the player's `distance()` to each pellet's world coordinates.
    *   If the distance is less than half a cell size, the pellet is considered "eaten."
    *   `pellet_pen.clearstamp(stamp_id)` removes the pellet's drawing from the screen.
    *   `del pellet_pen.stamps[(px,py)]` removes the pellet from the active dictionary, so it won't be checked again.

*   **Maze Interaction:**
    *   **Actors:** `actors.py` imports `Maze` to check for wall collisions (`is_wall`) and get the grid dimensions for pathfinding and wrapping.
    *   **Renderer:** `renderer.py` imports `Maze` to get the lists of wall, pellet, and power pellet coordinates (`maze.walls`, etc.) that it needs to draw.

---
## **IV. Pac-Man Movement**

*   **8-Directional Movement:** This is implemented through a combination of `main.py`'s `bind_controls` and `actors.py`'s `Player.move`. `bind_controls` detects simultaneous arrow key presses and queues a compound direction like `"up-left"`. The `move` function then uses this string. If the direction string contains "up," "down," "left," or "right," it adjusts `next_x` and `next_y` accordingly. For diagonal movement (e.g., "up-left"), the move distance is multiplied by `0.707` (an approximation of `1/sqrt(2)`) to normalize the speed, so Pac-Man doesn't move faster diagonally.

*   **Buffered Turning:**
    1.  Player presses a direction key. `player.queue_direction()` is called in `main.py`.
    2.  This stores the desired direction in `player.buffered_direction` and sets `player.buffer_timer` to `12` frames.
    3.  On every frame, `Player.move()` checks if `self.buffered_direction` has a value.
    4.  If it does, it checks if Pac-Man is within `TURN_TOLERANCE` (5 pixels) of a grid cell's exact center.
    5.  If he is, it then checks `can_step_grid` to see if the buffered turn is a valid move.
    6.  If all conditions are met, the player's `self.direction` is updated to the buffered direction, the player's position is "snapped" to the exact center of the cell to prevent drifting, and the buffer is cleared.
    7.  If the turn is not yet possible, `buffer_timer` is decremented. If it reaches zero, the buffered direction is discarded.

*   **Screen Wrapping:** This is handled at the end of `Player.move`. It checks if the player's x or y coordinate has exceeded the calculated boundaries of the maze. If it has, `self.setx()` or `self.sety()` is used to instantly teleport the player to the opposite boundary.

*   **Grid Alignment for Turns:** A turn is only allowed when `is_at_center_x` and `is_at_center_y` are both true. This is checked by seeing if the player's world `x` coordinate is within `TURN_TOLERANCE` pixels of the nearest grid line's world coordinate. This prevents the player from turning in the middle of a corridor.

*   **Speed Calculation:** The base speed is `PLAYER_MOVE_SPEED` (4.0 pixels per frame). When moving diagonally, this is multiplied by `0.707`, resulting in a speed of ~2.83 pixels per frame in both the x and y axes, for a combined vector magnitude of `sqrt(2.83^2 + 2.83^2) ≈ 4.0`. When a power pellet is eaten, `player.move_speed` is temporarily increased by `3` for 3 seconds.

---
## **V. Game Loop**

*   **60 FPS Loop Construction:** The game does not use a `while True` loop. It uses `screen.ontimer(callback, delay)`. The `game_loop` function, after running all its logic for one frame, ends by calling `screen.ontimer(lambda: game_loop(...), 1000 // 60)`. This tells the `turtle` scheduler to call `game_loop` again after approximately 16.67 milliseconds, creating a stable, non-blocking 60 FPS loop.

*   **Order of Operations per Frame:**
    1.  Update UI (Score, Lives).
    2.  Check for Victory Condition (`remaining_pellets == 0`).
    3.  Check for Pellet collisions, update score.
    4.  Check for Power Pellet collisions, update score, apply speed boost.
    5.  Execute `player.move()` (handles input, turning, collision, wrapping).
    6.  Loop through each ghost:
        a. Execute `ghost.move()` (updates speed/size, AI chooses target, moves ghost).
        b. Check for `player.distance(ghost)` collision.
        c. If collision, decrement lives, reset positions, or trigger Game Over.
    7.  `screen.update()`: Draw all the changes for the frame to the screen.
    8.  Schedule the next `game_loop` call with `screen.ontimer`.

*   **Score & Lives:**
    *   `player.score` and `player.lives` are integer attributes of the `Player` object.
    *   Score is incremented in `game_loop` when pellets are eaten (`+10` for regular, `+50` for power).
    *   Lives are decremented in `game_loop` when `player.distance(ghost)` is less than a threshold.
    *   The `score_panel` and `lives_panel` are responsible for displaying these values on the UI each frame.

*   **Victory & Game Over:**
    *   **Victory:** Detected at the start of `game_loop` if `len(pellet_pen.stamps)` is zero. It calls `show_victory()` which stops the loop.
    *   **Game Over:** Detected after a ghost collision if `player.lives` becomes 0 or less. It calls `show_game_over()` which stops the loop.

*   **Restart Implementation:** The `start_new_game` function in `main.py` is the key. It's passed as a callback all the way to `show_victory` and `show_game_over`. When the "RESTART" button is clicked:
    1.  The `handle_click` function calls `start_new_game`.
    2.  `start_new_game` performs a full reset: clears UI messages, redraws all pellets, resets player score/lives/speed, resets all actor positions.
    3.  Crucially, it then makes the initial call to `game_loop`, kicking off the gameplay again without ever exiting the `main` function or reloading the program.

---
## **VI. Rendering**

*   **Walls:** `Wall.draw()` iterates through `maze.walls` and uses `self.stamp()` with a square shape and "dodger blue" color to draw the maze layout efficiently. Stamping is much faster than drawing individual squares with the pen.

*   **Pellets & Power Pellets:**
    *   `Pellet.draw()` stamps a small (`0.2`) "gold" circle for each pellet.
    *   `PowerPellet.draw()` stamps a larger (`0.5`) "chartreuse" circle for each power pellet.
    *   This visual distinction is based entirely on the `shapesize` and `fillcolor` properties set in their respective `__init__` methods.

*   **HUD (Score, Lives):** The `UiPanel` class handles this. `write_score` and `write_lives` are called every frame. They clear any previous text written by that turtle instance and then use `self.write()` to render the new score and lives values in the UI panel on the right.

*   **Pac-Man & Ghosts:**
    *   **Pac-Man:** A yellow circle (`shape("circle")`, `shapesize(0.9)`). Its position is updated every frame by `self.goto(final_x, final_y)` in `Player.move`.
    *   **Ghosts:** They are squares (`shape("square")`). Their color is set in their specific subclass `__init__`. Ghost size is dynamic; `BaseGhost.move` calls `self.shapesize(0.9 + fraction_eaten * 0.3)`, making them grow from 0.9x the base size to 1.2x as the game progresses, adding to the "evolution" theme.

---
## **VII. Cross-File Interactions (Dependency Map)**

*   **`main.py` imports:**
    *   `turtle`: For screen setup and the main loop timer.
    *   `random`: To choose a random starting position for the player.
    *   `constants`: To get screen dimensions and maze layout constants. (WHY: To configure the game window and maze positioning).
    *   `renderer`: To create `Wall`, `Pellet`, `PowerPellet`, and `UiPanel` objects. (WHY: To draw the game).
    *   `actors`: To create `Player` and all four `Ghost` objects. (WHY: To create the game's interactive entities).
    *   `mazes`: To load the maze data structure (`get_maze`). (WHY: To define the level geometry and pellet locations).

*   **`actors.py` imports:**
    *   `turtle`: To be the base class for all `Actor`s.
    *   `collections.deque`: For efficient queue operations in BFS.
    *   `heapq`: For the priority queue in UCS.
    *   `constants`: For numerous gameplay values (`CELL_SIZE`, `PLAYER_MOVE_SPEED`, `TURN_TOLERANCE`, etc.). (WHY: To control actor movement, size, and behavior).
    *   `mazes` (from `Player.move`): This is a local import, used to access `self.maze.grid` for collision checks.

*   **`renderer.py` imports:**
    *   `turtle`: To be the base class for `Pen`.
    *   `mazes`: It imports `maze_level_1` and `get_maze` but only seems to use the `Maze` object passed to its `__init__`. (WHY: To get the coordinate lists of things to draw).
    *   `constants`: For `CELL_SIZE` and screen dimensions. (WHY: To correctly size and position UI elements).

*   **`mazes.py` imports:**
    *   `constants`: For `CELL_SIZE` and maze dimensions. (WHY: To correctly convert grid coordinates to world coordinates).

*   **`constants.py` imports:**
    *   None. It is the root of many dependencies.

**Flow of Data/Functionality:**
`constants.py` -> `mazes.py` -> `actors.py` & `renderer.py` -> `main.py`

1.  `constants` provides the basic numbers.
2.  `mazes` uses these constants to interpret the raw maze data and create a `Maze` object containing lists of world coordinates for walls and pellets.
3.  `renderer` takes the `Maze` object and draws everything based on those coordinate lists.
4.  `actors` uses the `Maze` object to understand the world for collision and pathfinding. They use constants for their own internal logic (speed, turn tolerance).
5.  `main` is the master conductor. It creates the `Maze`, gives it to the `renderer`s and `actor`s, binds them all together, and runs the `game_loop` that calls their `move` and `draw` methods.

---
## **VIII. `constants.py` Explained**

*   `CELL_SIZE = 20`
    *   **Controls:** The size in pixels of a single grid cell.
    *   **Effect:** Halving would make the maze tiny; doubling would make it huge, likely pushing it off-screen. Affects all coordinate calculations.

*   `SCREEN_WIDTH = 950`, `SCREEN_HEIGHT = 600`
    *   **Controls:** The dimensions of the game window.
    *   **Effect:** Changing these would require recalculating the UI panel layout and maze starting positions.

*   `MAZE_LEVEL_START_X = -440.0`, `MAZE_LEVEL_START_Y = 250.0`
    *   **Controls:** The pixel coordinate of the top-left corner of the maze grid.
    *   **Effect:** Changing these would shift the entire maze on the screen.

*   `PLAYER_MOVE_SPEED = 4`
    *   **Controls:** The player's base speed in pixels per frame.
    *   **Effect:** Halving would make the player very slow; doubling would make the game very fast and difficult.

*   `TURN_TOLERANCE = 5`
    *   **Controls:** How close (in pixels) the player needs to be to the center of a grid cell to be allowed to make a turn.
    *   **Effect:** Halving would make turning feel very precise and difficult. Doubling would make it feel sloppy, allowing turns far from an intersection.

*   `BUFFER_FRAMES = 12`
    *   **Controls:** The number of frames (at 60 FPS) that a player's input is "remembered" before it's discarded. This is 12/60 = 0.2 seconds.
    *   **Effect:** Halving would require more precise timing for pre-turning. Doubling would let the player queue a turn from very far away, which might feel unresponsive.

---

## **IX. Function Reference Table**

| File | Function/Method | Parameters | Returns | Calls | Called By | Purpose |
|---|---|---|---|---|---|---|
| `main.py` | `init_screen` | - | `turtle.Screen` | `turtle` methods | `main` | Creates the game window. |
| `main.py` | `bind_controls` | `screen`, `player` | `None` | `player.queue_direction`, `screen.onkeypress` | `start_new_game` | Sets up keyboard input. |
| `main.py` | `show_game_over`| `screen`, `ui_panel`, `cb` | `None` | `ui_panel.write`, `screen.onclick` | `game_loop` | Displays game over screen. |
| `main.py` | `show_victory` | `screen`, `ui_panel`, `cb` | `None` | `ui_panel.write`, `screen.onclick` | `game_loop` | Displays victory screen. |
| `main.py` | `reset_positions`| `player`, `ghosts`, `x`, `y` | `None` | `actor.goto` | `game_loop`, `start_new_game` | Resets actors to start pos. |
| `main.py` | `game_loop` | many | `None` | `actor.move`, `pen.clearstamp`, `screen.update` | `start_new_game`, itself | The main game update tick. |
| `actors.py`| `Player.move` | - | `None` | `maze.is_wall`, `can_step_grid`, `self.goto` | `game_loop` | Handles player movement & collision. |
| `actors.py`| `BaseGhost.move` | `px`, `py`, `pdir`, ... | `None` | `self.choose_next_target`, `self.goto` | `game_loop` | Handles ghost movement & AI. |
| `actors.py`| `BaseGhost.choose_next_target`| `px`, `py`, ... | `None` | `self.get_neighbors`, `self.get_best_neighbor` | `BaseGhost.move` | Decides ghost's next grid cell. |
| `actors.py`| `RedGhost.get_best_neighbor` | `neighbors`, `px`, ... | tuple | `self.path_neighbor_to` | `choose_next_target` | Finds shortest path to player. |
| `actors.py`| `BlueGhost.update_mode` | `dt`, `frac_eaten` | `None` | - | `BaseGhost.move` | Switches between Chase/Scatter. |
| `mazes.py` | `Maze.is_wall` | `x`, `y` | `bool` | - | `Player.move` | Checks for wall at pixel coordinate. |
| `renderer.py`| `Pellet.draw` | - | `None` | `self.goto`, `self.stamp` | `start_new_game` | Draws all pellets. |

---

## **X. Top 15 Viva Questions**

1.  **Q: How is the main game loop structured to maintain a consistent 60 FPS without blocking the program?**
    *   **A:** The game avoids a traditional `while True` loop. Instead, it uses the `turtle.Screen().ontimer(callback, delay)` method. The `game_loop` function, after executing all the logic for a single frame, schedules itself to be called again after `1000 // 60` milliseconds (approx. 16.67ms). This creates a recursive, non-blocking loop that yields control back to the turtle event system, ensuring the window remains responsive.

2.  **Q: Explain the "evolution" aspect of the game. How do the ghosts change over time?**
    *   **A:** The "evolution" is implemented in the `BaseGhost.move` method. On every frame, it calculates the fraction of pellets that have been eaten. This fraction is then used to linearly scale up each ghost's `move_speed` and `shapesize`. For example, a ghost's speed is `self.base_speed + fraction_eaten * 2.7`. This means as the player clears the maze, the ghosts become progressively faster and larger, increasing the difficulty.

3.  **Q: Describe the targeting logic for the Blue Ghost (`BlueGhost`). How is it different from the others?**
    *   **A:** The Blue Ghost is unique because it has a state machine with two modes: "scatter" and "chase". In "scatter" mode, it ignores the player and targets a fixed corner of the maze. In "chase" mode, it acts as a flanker. It calculates two points, one 4 cells to the left of Pac-Man (perpendicular to his direction) and one 4 cells to the right. It then targets the flank that is currently further away from itself, trying to trap the player.

4.  **Q: How does the game handle player input to allow for smooth "buffered" turns at intersections?**
    *   **A:** When a player presses a direction key, the game doesn't change direction immediately. It calls `Player.queue_direction`, which stores the desired direction in `self.buffered_direction` for 12 frames. In the `Player.move` method, it constantly checks if a buffered direction exists. If it does, and if the player is within a 5-pixel `TURN_TOLERANCE` of a grid cell's center, it validates the turn and executes it, snapping the player to the grid center. This lets players "pre-press" a turn before they arrive at the intersection.

5.  **Q: Walk me through the process of a pellet being eaten, from collision to removal.**
    *   **A:** In the `game_loop`, the code iterates through a dictionary of all active pellets. For each one, it calculates the pixel distance to the player using `player.distance()`. If this distance is less than half a cell size, it registers a collision. The player's score is increased by 10. Then, `pellet_pen.clearstamp()` is called with the pellet's stored `stamp_id` to remove it visually, and `del pellet_pen.stamps[...]` removes it from the dictionary so it's no longer processed.

6.  **Q: The Green Ghost (`GreenGhost`) uses a "minimax" algorithm. What does this mean in practice?**
    *   **A:** It means the Green Ghost is trying to "think ahead". Its `minimax_neighbor_to` function simulates a short, turn-based game to a depth of 3 moves. It evaluates which of its possible next moves will lead to the best position, assuming the player will then make the best possible move to escape. The "best" position for the ghost is one that minimizes distance to the player while also limiting the player's available escape routes. This makes it appear to be setting up an ambush rather than just blindly chasing.

7.  **Q: How is diagonal movement speed normalized for the player, and why is this important?**
    *   **A:** In `Player.move`, if the direction is diagonal (e.g., "up-left"), the movement distance for that frame is multiplied by `0.707`. This is an approximation of `1/sqrt(2)`. It's important because moving 1 pixel on X and 1 pixel on Y in one frame results in a total distance of `sqrt(2)` pixels. Normalizing the speed ensures the player's total speed is consistent whether they are moving cardinally or diagonally, preventing a speed exploit.

8.  **Q: How does the game restart without relaunching the application?**
    *   **A:** The `main` function defines an inner function, `start_new_game`, which encapsulates all the setup logic: resetting scores, redrawing pellets, and resetting actor positions. This function is passed as a callback to the `show_game_over` and `show_victory` screens. When the "RESTART" button is clicked, this callback is invoked, which re-initializes the game state and kicks off the `game_loop` again.

9.  **Q: Explain the collision detection logic for Pac-Man. Is it grid-based or pixel-based?**
    *   **A:** It's pixel-based and reactive. Instead of just checking the next grid cell, the `Player.move` method calculates the player's potential next pixel coordinate (`next_x`, `next_y`). It then checks for walls at the corners of the player's hitbox at that future position using `maze.is_wall()`. This allows for "sliding" behavior, where a player can move along a wall if the path is partially, but not fully, obstructed.

10. **Q: In `actors.py`, what is the purpose of `get_closest_valid_cell`?**
    *   **A:** It's a failsafe for the ghost AI. A ghost's target (e.g., a flanking position) might sometimes be calculated to be inside a wall. If a ghost tries to pathfind to an invalid cell, it could get stuck or throw an error. This function is called before pathfinding; if the target is invalid, it performs a quick BFS search to find the nearest accessible cell and uses that as the target instead.

11. **Q: What data structure in `renderer.py` is essential for removing eaten pellets, and why?**
    *   **A:** The `self.stamps` dictionary in the `Pellet` and `PowerPellet` classes. When a pellet is drawn using `self.stamp()`, turtle returns a unique `stamp_id`. This ID is stored in the dictionary, with the pellet's world coordinate as the key. When a pellet is eaten, the game loop uses the player's position to look up the coordinate in this dictionary, retrieve the correct `stamp_id`, and then call `self.clearstamp(stamp_id)` to remove the specific pellet that was eaten.

12. **Q: The Red Ghost uses BFS for pathfinding, while the Yellow Ghost uses DFS. What is the behavioral difference?**
    *   **A:** BFS (Breadth-First Search) explores the grid layer by layer, guaranteeing that it finds the absolute shortest path in terms of steps. This makes the Red Ghost a relentless and efficient chaser. DFS (Depth-First Search) explores one path as far as it can go before backtracking. This means it will find *a* path, but not necessarily the shortest one. This makes the Yellow Ghost's movement appear erratic, unpredictable, and inefficient, as it might take a long, winding route to the player.

13. **Q: How does the game handle screen-wrapping for actors?**
    *   **A:** For the player, it's handled in `Player.move`. After the player's position is updated, it checks if their new coordinates are beyond the maze boundaries. If so, it uses `self.setx()` or `self.sety()` to teleport them to the opposite side. For ghosts, it's handled at the grid level in `BaseGhost.handle_wrapping`, which uses the modulo operator to wrap their grid coordinates, and then updates their world position accordingly.

14. **Q: In `main.py`, why is `list(pellet_pen.stamps.items())` used in the game loop?**
    *   **A:** This is a crucial detail for safe iteration. The code is iterating through the pellets to check for collisions, and if a collision occurs, it deletes that pellet from the `pellet_pen.stamps` dictionary. Modifying a dictionary while iterating over it directly would raise a `RuntimeError` in Python. By converting the items to a `list` first, the loop iterates over a static copy, and the original dictionary can be safely modified.

15. **Q: What is the purpose of the rule that prevents ghosts from making 180-degree turns?**
    *   **A:** This is a classic rule from the original Pac-Man. In `BaseGhost.choose_next_target`, after getting a list of valid neighbors, the code filters out the neighbor that corresponds to the ghost's previous grid cell. This forces the ghost to always move forward at an intersection and prevents them from getting "stuck" in a two-square hallway by just turning back and forth. It makes their movement more predictable and less erratic.

---

## **XI. Gotchas & Subtle Code Sections**

*   **Diagonal Speed Normalization:** A student might forget to explain *why* the diagonal speed is multiplied by `0.707`. It's to ensure the vector magnitude of the speed is constant.
*   **Pixel vs. Grid Collision:** The fact that the player uses pixel-based collision while ghosts use grid-based pathfinding is a key distinction. The player's method allows for "sliding," while the ghosts' method is about proactive decision-making.
*   **`list(dict.items())` for Deletion:** This is a subtle but critical Python pattern to avoid a `RuntimeError`. A student should be able to explain *why* this is necessary.
*   **Coordinate System Inversion:** The maze grid `(0,0)` is top-left, while turtle's `(0,0)` is center, with Y increasing upwards. The formulas in `grid_to_world` and `world_to_grid` explicitly handle this inversion for the Y-coordinate.
*   **`ontimer` Loop vs. `while` Loop:** A core architectural choice. The student should be able to explain that `ontimer` is non-blocking and integrates with the `turtle` event system, which is superior to a blocking `while True` loop for a GUI application.
*   **Diagonal "Corner Squeezing" Prevention:** The check in `can_step_grid` that ensures `is_open_cell(gx + dx, gy, grid) and is_open_cell(gx, gy + dy, grid)` for diagonal moves is a subtle but important rule for correct 8-way movement on a grid.
*   **Restart via Callback:** The restart mechanism doesn't involve complex state management; it's just a simple and elegant use of a function callback passed through multiple layers of the call stack.
*   **Blue Ghost's Flanking Logic:** The flank target is determined by `(-dy, dx)` and `(dy, -dx)`, which are perpendicular vectors to the player's movement direction. The ghost then targets the flank *further* from itself, which is a non-obvious but clever heuristic to promote pincer movements.
*   **Local Import in `Player.move`:** The `from constants import ...` is inside the `move` method. While unusual, it's valid. This might be a point of discussion about code style, though it has no functional impact here.
