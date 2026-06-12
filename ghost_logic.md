# GHOST LOGIC — Complete Guide (Pac-Man Evolution)

This document explains **everything** about how ghosts work in this code. You do not need to look at any source file to understand it — every function, variable, and rule from the actual code is explained here.

---

## 1. WHAT IS A GHOST (in this code)

### The Class Hierarchy

```
turtle.Turtle  (Python's built-in drawing turtle)
    └── Actor  (our base for anything that moves)
            └── BaseGhost  (shared ghost brain and body — 90% of all logic)
                    ├── RedGhost    (chaser — uses BFS pathfinding)
                    ├── YellowGhost (wanderer — uses DFS pathfinding)
                    ├── GreenGhost  (ambusher — uses Minimax AI)
                    └── BlueGhost   (flanker — uses UCS with scatter/chase mode)
```

### What is a Ghost — in simple terms

A ghost is a **turtle** (a visible shape on the screen) that has:
- A position on the screen (inherited from Turtle)
- A position in the maze grid (`gx`, `gy`)
- A target in the maze grid where it wants to go next (`next_gx`, `next_gy`)
- A previous position so it does not turn back on itself (`prev_gx`, `prev_gy`)
- A speed that grows over time (`base_speed` + bonus based on pellets eaten)
- A size that also grows over time
- A personal AI strategy for picking which way to go

### Every Attribute a Ghost Has

These are set in `BaseGhost.__init__` and used by every ghost:

| Attribute | Type | Purpose |
|---|---|---|
| `self.maze` | `Maze` object | Store the maze grid so the ghost can check walls and navigate |
| `self.gx` | `int` | Ghost's current column in the maze grid (0 = leftmost) |
| `self.gy` | `int` | Ghost's current row in the maze grid (0 = topmost) |
| `self.start_gx` | `int` | Ghost's spawn column — used when resetting after death |
| `self.start_gy` | `int` | Ghost's spawn row |
| `self.next_gx` | `int` | Column of the cell the ghost is currently walking toward |
| `self.next_gy` | `int` | Row of the cell the ghost is currently walking toward |
| `self.target_x` | `float` | Pixel x-coordinate of the current target cell center |
| `self.target_y` | `float` | Pixel y-coordinate of the current target cell center |
| `self.prev_gx` | `int` | The column the ghost was at BEFORE its current cell (for 180° prevention) |
| `self.prev_gy` | `int` | The row the ghost was at BEFORE its current cell |
| `self.base_speed` | `float` | Starting speed (different per ghost: 2.0–2.3) |
| `self.move_speed` | `float` | Actual speed right now (base + bonus from pellets eaten) |

Attributes added by specific ghosts:

| Attribute | Ghost | Type | Purpose |
|---|---|---|---|
| `self.mode` | BlueGhost only | `str` | `"scatter"` or `"chase"` |
| `self.mode_timer` | BlueGhost only | `float` | Seconds spent in current mode |

### How Many Ghosts — How They Are Created

**Exactly 4 ghosts**, created in `main.py`:

```python
red_ghost = RedGhost(maze, 1, 1)          # top-left area
yellow_ghost = YellowGhost(maze, 31, 1)   # top-right area
green_ghost = GreenGhost(maze, 1, 23)     # bottom-left area
blue_ghost = BlueGhost(maze, 31, 23)      # bottom-right area
```

The four ghosts start at the **four corners** of the playable maze area. Coordinates `(gx, gy)` refer to the grid in `mazes.py`. Each ghost is told its starting cell when created — this is also where it returns when Pac-Man dies.

### What Makes Each Ghost Different — at the Code Level

Each ghost is a **separate class** that inherits from `BaseGhost`. The only method they override is `get_best_neighbor(neighbors, player_x, player_y, player_dir, remaining_pellets)`.

In other words: every ghost shares the same movement physics, the same wall-avoidance logic, the same speed/size scaling, the same 180° turn prevention — but each one has a **different answer** to the question: "Which of these valid neighboring cells should I go to next?"

---

## 2. THE GHOST BRAIN — STATE MACHINE

### What States Exist

**Most ghosts (Red, Yellow, Green):** Have only **one state** — they always chase.

**Blue Ghost:** Has **two states** — `"scatter"` and `"chase"`. It switches between them on a timer.

**Frightened mode: DOES NOT EXIST in this game.** Power pellets give Pac-Man a speed boost but do NOT make ghosts blue or scared. This is a major difference from the original Pac-Man. A student should be prepared to explain this design choice.

**Eaten/respawning state: DOES NOT EXIST in this game.** When a ghost touches Pac-Man, Pac-Man loses a life and everyone resets positions. Ghosts are never "eaten."

### Blue Ghost's State Diagram

```
                            fraction_eaten increases,
                            scatter_duration shrinks
                                    │
                                    ▼
    ┌──────────┐     timer runs out     ┌──────────┐
    │ SCATTER  │ ─────────────────────→ │  CHASE   │
    │           │                       │           │
    │ target =  │ ←─────────────────────│ target = │
    │ bottom-   │     timer runs out    │ flank    │
    │ right     │     (fixed 20 sec)    │ position │
    │ corner    │                       │ relative │
    └──────────┘                       │ to Pac-  │
                                        │ Man      │
                                        └──────────┘
```

### Blue Ghost State Machine — Exact Details

```
update_mode(dt, fraction_eaten):
    scatter_duration = max(1.0, 7.0 - fraction_eaten * 6.0)
    chase_duration = 20.0

    if mode == "scatter":
        if mode_timer >= scatter_duration:
            mode = "chase"
            mode_timer = 0.0
    else:  # mode == "chase"
        if mode_timer >= chase_duration:
            mode = "scatter"
            mode_timer = 0.0
```

**Scatter duration shrinks as more pellets are eaten.** At game start (0% eaten) it lasts 7 seconds. At 100% eaten it lasts `max(1.0, 7.0 - 6.0) = 1.0` second. This is part of the difficulty scaling.

**Chase duration is always 20 seconds**, no matter what.

---

## 3. HOW A GHOST MOVES — STEP BY STEP

Think of a ghost like a taxi driver who:
1. Knows their current street intersection (grid cell)
2. Has a destination in mind (target cell)
3. Drives toward the next intersection
4. When they arrive at an intersection, checks: "Which way gets me closer to my target?"
5. Picks a direction and drives to the next intersection
6. Repeats forever

### Coordinate Systems — The Ghost Uses TWO

**Grid coordinates** `(gx, gy)` — Which cell in the maze. `gx` = column (0..32), `gy` = row (0..24). Row 0 is the top of the screen.

**World/pixel coordinates** `(x, y)` — Where the turtle is drawn on screen. `x` increases to the right, `y` increases upward.

The ghost keeps both. Its grid position `(gx, gy)` is where it is in the maze logic. Its turtle position `xcor(), ycor()` is where it appears on screen.

Converting between them:

```
grid → world:  x = MAZE_LEVEL_START_X + gx * CELL_SIZE
               y = MAZE_LEVEL_START_Y - gy * CELL_SIZE
               (subtract gy because row 0 is top, but turtle y increases upward)

world → grid:  gx = int((x - MAZE_LEVEL_START_X + CELL_SIZE//2) / CELL_SIZE)
               gy = int((MAZE_LEVEL_START_Y - y + CELL_SIZE//2) / CELL_SIZE)
```

**NOTE:** The `+ CELL_SIZE//2` (which equals +10) is the rounding offset. It means: "if the pixel position is closer to this cell's center than the neighbor's, you are in this cell."

---

### The Movement Recipe — Every Frame

Here is exactly what happens in `BaseGhost.move()` every frame, in order:

---

#### STEP 1: Calculate Difficulty Scaler

```python
fraction_eaten = (total_pellets - remaining_pellets) / total_pellets
```

This is a number from `0.0` (no pellets eaten yet) to nearly `1.0` (almost all pellets eaten).

---

#### STEP 2: Update Speed and Visual Size

```python
self.move_speed = self.base_speed + fraction_eaten * 2.7
self.shapesize(0.9 + fraction_eaten * 0.3)
```

**Speed example:** Red Ghost has `base_speed = 2.0`. At start, speed = 2.0 pixels/frame. At 100% eaten, speed = 2.0 + 2.7 = 4.7 pixels/frame.

**Size example:** At start, `shapesize(0.9)` — 90% of default. At 100% eaten, `shapesize(1.2)` — 120% of default.

---

#### STEP 3: (Blue Ghost Only) Update Mode Timer

```python
if hasattr(self, "update_mode"):
    self.update_mode(1/60, fraction_eaten)
```

This adds 1/60th of a second (~16.7 ms) to Blue Ghost's mode timer and may switch it between scatter and chase.

---

#### STEP 4: Check If We've Reached Our Target Cell

```python
x, y = self.xcor(), self.ycor()
dist = sqrt((self.target_x - x)**2 + (self.target_y - y)**2)

if dist < self.move_speed:
```

The ghost checks: "Am I close enough to my target pixel position that I'll overshoot it this frame?" If yes:

---

#### STEP 5: Snap to Target, Update Position, Choose New Target

```python
self.goto(self.target_x, self.target_y)       # snap exactly to cell center
self.gx = self.next_gx                         # "I am now at the cell I was walking toward"
self.gy = self.next_gy
self.handle_wrapping()                         # wrap if we went off the maze edge
self.choose_next_target(player_x, player_y,    # DECISION TIME: pick next cell
                        player_dir, remaining_pellets)
self.target_x, self.target_y =                 # set new target pixel position
    self.grid_to_world(self.next_gx, self.next_gy)
```

**This is the key moment.** When the ghost snaps to a cell center, it makes the decision about where to go next. `choose_next_target` is where the AI happens.

---

#### STEP 6: Move Toward Current Target

```python
x, y = self.xcor(), self.ycor()
dx = self.target_x - x
dy = self.target_y - y
dist = sqrt(dx**2 + dy**2)

if dist > 0:
    step = min(self.move_speed, dist)    # don't overshoot
    step_x = (dx / dist) * step          # unit vector × step size
    step_y = (dy / dist) * step
    self.goto(x + step_x, y + step_y)    # move a little closer
```

The ghost moves in a **straight line** toward the target cell center. The movement is pixel-smooth, not grid-snapping. It moves `move_speed` pixels per frame, but if it's closer than that, it just moves the remaining distance.

---

### The Decision Moment — How `choose_next_target` Works

This is the ghost's brain:

```
choose_next_target(player_x, player_y, player_dir, remaining_pellets):
    1. neighbors = self.get_neighbors(self.gx, self.gy)
       → Find all 8 cells around me that I can legally step into

    2. Remove the cell I just came from (180° prevention)
       IF len(neighbors) > 1 AND I have a previous position:
           filter out the neighbor that wraps to (prev_gx, prev_gy)

    3. IF no neighbors left (dead end):
           keep the unfiltered list (allow reversing)

    4. Save current (gx, gy) as (prev_gx, prev_gy)

    5. best = self.get_best_neighbor(neighbors, player_x, player_y,
                                     player_dir, remaining_pellets)
       → Let the ghost-specific AI choose the winner

    6. self.next_gx, self.next_gy = best
       → "That's where I'm going next"
```

**Why the 180° prevention rule?** Without it, a ghost could go left → right → left → right in a 2-cell hallway. That looks broken. Original Pac-Man has this same rule.

**Real-world analogy:** Imagine you're walking down a hallway and come to an intersection. You can go left, right, or straight. You CAN'T do a 180° U-turn at the intersection (unless it's the only option). You must go forward.

---

### How Walls Block the Ghost

The ghost's `get_neighbors` method checks every direction using `can_step_grid`:

```python
def can_step_grid(gx, gy, dx, dy, grid):
    nx = gx + dx
    ny = gy + dy
    if not is_open_cell(nx, ny, grid):
        return False               # DESTINATION IS A WALL → BLOCKED
    
    if dx != 0 and dy != 0:
        # DIAGONAL MOVE: check that BOTH cardinal neighbors are also open
        if not is_open_cell(gx + dx, gy, grid):
            return False
        if not is_open_cell(gx, gy + dy, grid):
            return False
    
    return True
```

**For diagonal moves, the ghost checks THREE cells:**
1. The destination cell (must be open)
2. The cardinal cell to the right/left
3. The cardinal cell above/below

This prevents the ghost from sliding diagonally through a gap that is only 1 cell wide.

```
    GOOD:                         BAD (blocked):
    . . . . . .                   . X . . .
    . . G . . .   G can move      . G . . .   G cannot move up-left
    . . . P . .   up-right        . . P . .   because the cell above
    . . . . . .                   . . . . .   is a wall
```

---

## 4. THE TARGET SYSTEM — WHERE EACH GHOST WANTS TO GO

### Ghost Speed Comparison (Base Speeds)

| Ghost | base_speed | max_speed | Color |
|---|---|---|---|
| Red | 2.0 | 4.7 | red |
| Yellow | 2.2 | 4.9 | orange |
| Green | 2.1 | 4.8 | medium spring green |
| Blue | 2.3 | 5.0 | cyan |

---

### Red Ghost — The Chaser (BFS)

**Personality:** Relentless. Takes the shortest path to where you are RIGHT NOW.

**Target cell:** Pac-Man's current grid cell `(pgx, pgy)`.

**How it chooses direction:**

```
RedGhost.get_best_neighbor(neighbors, player_x, player_y, ...):
    pgx, pgy = self.world_to_grid(player_x, player_y)
    return self.path_neighbor_to(neighbors, (pgx, pgy))
```

`path_neighbor_to` runs **BFS** (Breadth-First Search) from the ghost's current cell to Pac-Man's cell. BFS guarantees the **shortest path in terms of number of steps**. It then picks the neighbor that is the first step on that path.

**Real-world analogy:** Red is the taxi driver with a GPS that always recalculates the shortest route to your current location. If you turn a corner, red immediately finds a new shortest route.

**ASCII Example:**
```
P=Pac-Man  R=Red Ghost  . = open  X = wall  T = target (Pac-Man cell)

    . . . . . . . .
    . P . . . . . .
    . . X X X . . .
    . . . . X . . .
    . . . . X . . .
    . R . . X . . .
    
Red at (1,5), Pac-Man at (1,1)
BFS finds path: (1,5)→(1,4)→(1,3)→(1,2)→(1,1)
Red goes UP (straight toward Pac-Man)
```

---

### Yellow Ghost — The Wanderer (DFS)

**Personality:** Erratic. Takes paths that seem random and inefficient.

**Target cell:** Pac-Man's current grid cell `(pgx, pgy)`.

**How it chooses direction:**

```
YellowGhost.get_best_neighbor(neighbors, player_x, player_y, ...):
    pgx, pgy = self.world_to_grid(player_x, player_y)
    return self.dfs_neighbor_to(neighbors, (pgx, pgy))
```

`dfs_neighbor_to` runs **DFS** (Depth-First Search) from the ghost's current cell to Pac-Man's cell. DFS explores by going **as far as possible down one path before trying another**. This means it often finds a very long, winding path rather than the shortest one.

**Real-world analogy:** Yellow is like someone who enters a maze and always turns left. They'll eventually reach you, but they might take a very weird route through the entire maze first.

**Why is DFS here?** In the original Pac-Man, ghosts with different pathfinding created interesting variety. DFS creates a ghost that feels less "smart" and more unpredictable — useful at early difficulty levels.

**ASCII Example — DFS vs BFS:**
```
P=Pac-Man  Y=Yellow Ghost  . = open  X = wall  # = DFS path

    . . . . . . . .
    . P . . . . . .
    . . . . . . . .
    X X X X . X X X
    . . . . . . . .
    . . . . . . . .
    Y . . . . . . .

DFS might go RIGHT first (exploring the right side of the maze deeply)
before ever going up toward Pac-Man. BFS would go UP immediately.
```

**NOTE:** DFS is not guaranteed to find the shortest path. It finds A path, often a long one. This makes Yellow appear to have a mind of its own.

---

### Green Ghost — The Ambusher (Minimax)

**Personality:** Thinks ahead. Tries to cut off your escape routes.

**Target cell:** It doesn't just target a cell — it evaluates which direction leads to the best future position by simulating ghost and Pac-Man moves 3 steps ahead.

**How it chooses direction:**

```
GreenGhost.get_best_neighbor(neighbors, player_x, player_y, ...):
    pgx, pgy = self.world_to_grid(player_x, player_y)
    return self.minimax_neighbor_to(neighbors, (pgx, pgy))
```

`minimax_neighbor_to` simulates a 3-move game:
1. The ghost picks a direction (the ghost wants to MAXIMIZE a score)
2. Pac-Man picks a direction to escape (simulated Pac-Man wants to MINIMIZE that same score)
3. The ghost picks another direction
4. Repeat up to 3 total moves (depth=3)

The score being optimized is:

```python
def score_position(ghost_cell, pac_cell):
    distance_score = -octile_distance(ghost_cell, pac_cell)
    escape_routes = len(legal_steps(pac_cell))
    return distance_score - escape_routes * 0.35
```

Score = (negative distance to Pac-Man) − (Pac-Man's escape options × 0.35)

**This means the ghost wants to be CLOSE to Pac-Man while also CORNERING Pac-Man** (reducing his escape options).

**Real-world analogy:** Green is a chess player thinking 3 moves ahead. While Red just chases you, Green moves to cut off your escape routes. It's like a basketball defender who doesn't just follow you — they position themselves to block your passing lanes.

**ASCII Example:**
```
    . . . . . . . .
    . P . . . . . .
    . . . . . . . .
    . . G . . . . .
    . . . . . . . .
    . . . . . . . .
    
From (2,2), Green can go to (2,1), (2,3), (1,2), or (3,2).
Minimax evaluates each option 3 moves deep.
Going to (2,1) might score higher because from there,
Green can reach (1,1) in one more move while Pac-Man
at (1,0) would have only 2 escape routes.
```

---

### Blue Ghost — The Flanker (UCS with Scatter/Chase Modes)

**Personality:** A two-mode ghost. Sometimes it attacks from the side, sometimes it retreats to a corner.

**Two modes:**

| Mode | Target |
|---|---|
| `"scatter"` | Bottom-right corner: `(cols-2, rows-2)` = `(31, 23)` on a 33×25 grid |
| `"chase"` | A flank position relative to Pac-Man's direction |

**How chase mode calculates the flank target:**

```python
dx, dy = direction_to_delta(player_dir)
# dx, dy = which way Pac-Man is moving

if dx == 0 and dy == 0:
    # Pac-Man is stopped — target Pac-Man directly
    target = (pgx, pgy)
else:
    left_flank  = (-dy, dx)    # rotate direction LEFT  90 degrees
    right_flank = (dy, -dx)    # rotate direction RIGHT 90 degrees
    
    left_target  = (pgx + left_flank[0]  * 4, pgy + left_flank[1]  * 4)
    right_target = (pgx + right_flank[0] * 4, pgy + right_flank[1] * 4)
    
    # Pick the flank FARTHER from the ghost
    ghost_cell = (self.gx, self.gy)
    left_score  = distance(ghost_cell, left_target)
    right_score = distance(ghost_cell, right_target)
    target = left_target if left_score >= right_score else right_target
```

**What this does:** Blue picks a cell 4 steps to Pac-Man's left or right side, choosing the side that is farther from Blue's current position. This makes Blue go AROUND to the far side, attempting to trap Pac-Man between himself and the other ghosts.

**Blue uses UCS (Uniform Cost Search)** for pathfinding, which finds the shortest path where diagonal steps cost 1.414 and cardinal steps cost 1.0. This is like BFS but accounts for diagonal movement being physically longer.

**Real-world analogy:** Blue is the friend who doesn't chase you directly but instead runs to the other side of the building to cut you off when you come out. The scatter mode is like taking a break — they give up and sit in a corner for a while.

**ASCII Example — Flank Position:**
```
Pac-Man at (5, 3) moving RIGHT  (dx=1, dy=0)
left_flank  = (-0, 1) = (0, 1)   → target = (5+0, 3+4) = (5, 7)
right_flank = (-1, 0) = (-1, 0)  → target = (5-4, 3+0) = (1, 3)

Blue is at (0, 0). Distance to (5,7) = 12. Distance to (1,3) = 4.
Blue picks (5,7) — the FARTHER flank — and goes around.

    . . . . . . . . . .
    . B . . . . . . . .    B = Blue Ghost
    . . . . . . . . . .    P = Pac-Man (moving RIGHT)
    . . . . P → . . . .    T = chosen target (the far flank)
    . . . . . . . . . .
    . . . . . . . . . .
    . . . . . . . . . .
    . . . . . . . .T. .    Blue goes the long way around
```

---

## 5. HOW GHOSTS INTERACT WITH THE MAZE / WALLS

### Maze Data Structure

The maze is stored as a **list of strings** in `mazes.py`:

```python
maze_level_1 = [
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX",   # row 0
    "X...............O...............X",   # row 1
    ...
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX"    # row 24
]
```

Each character in each string is one cell.

| Character | Meaning |
|---|---|
| `"X"` | Wall — impassable |
| `"."` | Pellet — open passage with food |
| `"O"` | Power pellet — open passage with power food |
| `" "` (space) | Empty open passage |

The grid is 33 columns wide × 25 rows tall.

### Wall Check — Exact Logic

When a ghost considers stepping into cell `(nx, ny)`:

```python
def is_open_cell(gx, gy, grid):
    wx = (gx + cols) % cols    # wrap coordinates if needed
    wy = (gy + rows) % rows
    return grid[wy][wx] != "X"   # is it NOT a wall?
```

That's it. If `grid[row][column]` is `"X"`, the cell is closed. Anything else is open.

**NOTE:** The ghost doesn't need to check pellets or power pellets — those are open spaces. Only `"X"` blocks movement.

### Coordinate Conversion — Exact Formulas

**Ghost pixel position → grid cell:**

```python
gx = int((x - MAZE_LEVEL_START_X + CELL_SIZE // 2) / CELL_SIZE)
gy = int((MAZE_LEVEL_START_Y - y + CELL_SIZE // 2) / CELL_SIZE)
```

Where `x` and `y` come from `self.xcor()` and `self.ycor()` (the turtle's current position on screen).

**Worked example:**

```
MAZE_LEVEL_START_X = -440.0
MAZE_LEVEL_START_Y = 250.0
CELL_SIZE = 20

Ghost pixel position: x = -320, y = 200

gx = int((-320 - (-440) + 10) / 20)
   = int((-320 + 440 + 10) / 20)
   = int(130 / 20)
   = int(6.5)
   = 6

gy = int((250 - 200 + 10) / 20)
   = int(60 / 20)
   = 3

Ghost is in cell (6, 3) → column 6, row 3
```

### Maze Edge Wrapping

Ghosts DO wrap around the maze edges, just like Pac-Man:

```python
def handle_wrapping(self):
    grid_rows = len(self.maze.grid)
    grid_cols = len(self.maze.grid[0])

    if self.gx < 0:                     # left edge → right
        self.gx = grid_cols - 1
        tx, ty = self.grid_to_world(self.gx, self.gy)
        self.goto(tx, ty)               # teleport
    elif self.gx >= grid_cols:          # right edge → left
        self.gx = 0
        tx, ty = self.grid_to_world(self.gx, self.gy)
        self.goto(tx, ty)
    # same for gy: top → bottom, bottom → top
```

**NOTE:** The ghost teleports immediately when its grid position goes out of bounds. This happens BEFORE the next decision, so the ghost can pathfind through the tunnel.

### Can Ghosts Walk Through Each Other?

**Yes.** There is no collision detection between ghosts. They overlap freely. The only collision check is between each ghost and Pac-Man.

### Ghost House, One-Way Paths, Forbidden Cells

**None of these exist.** This is a simplified Pac-Man. There is no ghost house, no one-way gates, no special zones. Every open cell is accessible to every ghost at all times.

### Walkthrough: Collision Check Example

```
Maze segment (grid = mazes.py):

    Row 6: "X.XX...XX...XX.XX...XX...XX.X"
    Row 7: "X.XX...XX...XX.XX...XX...XX.X"
    Row 8: "X..............................X"
    Row 9: "X.XX...XX...XX.XX...XX...XX.X"
    
Ghost at world position (-300, 120), wants to move UP (dx=0, dy=-1).
Ghost checks destination cell.

1. Convert ghost position to grid:
   gx = int((-300 + 440 + 10) / 20) = int(150/20) = 7
   gy = int((250 - 120 + 10) / 20) = int(140/20) = 7
   Ghost is at grid (7, 7).

2. Destination cell: (7, 7-1) = (7, 6)
   But gy=6, row 6. Check grid[6][7]:
   grid[6] = "X.XX...XX...XX.XX...XX...XX.X"
   grid[6][7] = 'X' (a wall!)

3. can_step_grid returns False.
   Ghost does NOT include (7,6) in its neighbor list.
   The ghost cannot go UP from here.
```

---

## 6. HOW GHOSTS INTERACT WITH PAC-MAN

### Collision Detection — Exact Condition

In `main.py`'s `game_loop`, after every ghost moves:

```python
if player.distance(ghost) < CELL_SIZE * 0.8:
```

`player.distance(ghost)` is a Turtle method that returns the Euclidean pixel distance between the center of the player turtle and the center of the ghost turtle.

`CELL_SIZE * 0.8 = 20 * 0.8 = 16 pixels`.

So: **if the centers of Pac-Man and the ghost are less than 16 pixels apart, it's a collision.**

Since each actor is drawn at approximately 0.9× cell size (18 pixels), the collision radius of 16 pixels means they overlap by about 2 pixels when collision triggers. This gives a small margin so it doesn't feel unfair.

### What Happens on Collision

```python
player.lives -= 1

if player.lives > 0:
    reset_positions(player, ghosts, player_start_x, player_start_y)
    # All actors teleport to their starting positions, game continues
else:
    show_game_over(screen, ui_panel, restart_callback)
    return
    # Game stops, RESTART button appears
```

**There is no distinction between "ghost eats Pac-Man" and "Pac-Man eats ghost."** The ghosts are never frightened, so every ghost-on-Pac-Man collision is a life lost for the player.

### The Reset Sequence

`reset_positions` does the following:

```python
# 1. Teleport player to start position, stop movement, clear buffer
player.goto(player_start_x, player_start_y)
player.direction = "stop"
player.buffered_direction = None

# 2. For each ghost:
for ghost in ghosts:
    # Convert ghost's spawn grid cell to world coordinates
    start_x, start_y = ghost.grid_to_world(ghost.start_gx, ghost.start_gy)
    ghost.goto(start_x, start_y)       # teleport to spawn
    ghost.gx = ghost.start_gx          # reset grid position
    ghost.gy = ghost.start_gy
    ghost.next_gx = ghost.start_gx      # reset next target
    ghost.next_gy = ghost.start_gy
    ghost.target_x = start_x            # reset target pixel position
    ghost.target_y = start_y
    
    # Delete previous-position data so 180° rule doesn't interfere
    if hasattr(ghost, "prev_gx"):
        del ghost.prev_gx
    if hasattr(ghost, "prev_gy"):
        del ghost.prev_gy
```

**Everything resets.** The player goes back to their random starting pellet. All four ghosts go back to their four corners. Ghost AI starts fresh (no stored previous position, so they don't try to reverse back to where they were before the reset).

---

## 7. FRIGHTENED MODE — FULL BREAKDOWN

### Frightened Mode: DOES NOT EXIST

This is the single most important thing to understand about this codebase:

**Power pellets do NOT make ghosts frightened.**

When Pac-Man eats a power pellet (`"O"` in the maze), this happens in `game_loop`:

```python
# Power pellet eaten:
player.score += 50
player.move_speed += 3
screen.ontimer(player.reset_speed, 3000)
```

That is ALL. Score goes up by 50. Player gets +3 speed for 3 seconds. **Ghosts are not affected at all.**

There is no:
- Frightened state
- Color change to blue
- Movement reversal
- Random direction selection
- Increased ghost speed reduction
- Ghost-edible collision mode

This is a major design departure from the original Pac-Man. The game's challenge comes from the ghosts getting faster and larger as the maze empties, not from frightened mode management.

---

## 8. DIFFICULTY SCALING — HOW GHOSTS GET HARDER

### The Core Mechanism

Every frame, inside `BaseGhost.move()`:

```python
fraction_eaten = (total_pellets - remaining_pellets) / total_pellets
```

This is the percentage of the maze that has been cleared (0.0 to 1.0).

### Speed Scaling

```python
self.move_speed = self.base_speed + fraction_eaten * 2.7
```

| Ghost | base_speed | At 0% eaten | At 50% eaten | At 100% eaten |
|---|---|---|---|---|
| Red | 2.0 | 2.0 | 3.35 | 4.7 |
| Yellow | 2.2 | 2.2 | 3.55 | 4.9 |
| Green | 2.1 | 2.1 | 3.45 | 4.8 |
| Blue | 2.3 | 2.3 | 3.65 | 5.0 |

Compare to the player's speed: **always 4.0** (boosted to 7.0 for 3 seconds after a power pellet).

At the start, the player (speed 4) is faster than all ghosts (speed 2.0–2.3). By ~70% completion, ghosts start to match or exceed the player's speed. By 100% completion, all ghosts are faster than the player.

### Size Scaling

```python
self.shapesize(0.9 + fraction_eaten * 0.3)
```

- At 0%: `shapesize(0.9)` → 18×18 pixel square
- At 50%: `shapesize(1.05)` → 21×21 pixel square
- At 100%: `shapesize(1.2)` → 24×24 pixel square

**NOTE:** The size scaling is visual ONLY. Collision is checked using `player.distance(ghost) < CELL_SIZE * 0.8` which is a fixed 16-pixel radius regardless of ghost size. Bigger ghosts LOOK scarier but don't actually have bigger hitboxes.

However, because both speed AND size increase:
- Ghosts move faster (harder to dodge)
- Ghosts appear larger (psychological pressure)
- At high `fraction_eaten`, the visual overlap between ghost and player is more likely, even if the collision math is unchanged

### Blue Ghost's Scatter Duration Shrinks

```python
scatter_duration = max(1.0, 7.0 - fraction_eaten * 6.0)
```

- At 0%: 7.0 seconds (plenty of time in scatter / breathing room)
- At 50%: `max(1.0, 7.0 - 3.0)` = 4.0 seconds
- At 100%: `max(1.0, 7.0 - 6.0)` = 1.0 second (barely any scatter time)

As the game progresses, Blue Ghost spends more time in aggressive chase mode and less time in passive scatter mode.

---

## 9. GHOST RESPAWN — WHAT HAPPENS AFTER BEING EATEN

### Respawning: NOT IMPLEMENTED

Ghosts are never "eaten" in this game. Since there is no frightened mode, there is no scenario where Pac-Man eats a ghost.

However, ghosts DO reset positions when **Pac-Man dies** (Section 6 explains this). That reset sends all ghosts back to their starting corners. This is not a respawn in the traditional sense — it's a full round reset.

---

## 10. QUICK REFERENCE CHEAT SHEET

### Ghost Comparison Table

| Ghost | Nickname | Target (Normal) | Target (Chase Mode) | Algorithm | base_speed |
|---|---|---|---|---|---|
| Red | The Chaser | Pac-Man's current cell | (same) | BFS (shortest path) | 2.0 |
| Yellow | The Wanderer | Pac-Man's current cell | (same) | DFS (any path) | 2.2 |
| Green | The Ambusher | Minimax evaluation 3 moves ahead | (same) | Minimax depth=3 | 2.1 |
| Blue | The Flanker | Flank position 4 cells sideways from Pac-Man | Bottom-right corner (scatter) | UCS (weighted shortest) | 2.3 |

### Ghost Variable Table

| Variable | Lives In | Type | Controls |
|---|---|---|---|
| `gx` | BaseGhost | `int` | Current grid column (0 = left) |
| `gy` | BaseGhost | `int` | Current grid row (0 = top) |
| `start_gx` | BaseGhost | `int` | Spawn column — where ghost resets to |
| `start_gy` | BaseGhost | `int` | Spawn row — where ghost resets to |
| `next_gx` | BaseGhost | `int` | Column of the cell ghost is walking toward |
| `next_gy` | BaseGhost | `int` | Row of the cell ghost is walking toward |
| `target_x` | BaseGhost | `float` | Pixel x of the target cell center |
| `target_y` | BaseGhost | `float` | Pixel y of the target cell center |
| `prev_gx` | BaseGhost | `int` | Previous column (for 180° turn prevention) |
| `prev_gy` | BaseGhost | `int` | Previous row (for 180° turn prevention) |
| `base_speed` | BaseGhost (set by each subclass) | `float` | Starting speed (2.0–2.3) |
| `move_speed` | BaseGhost | `float` | Current speed = base + fraction_eaten × 2.7 |
| `maze` | BaseGhost | `Maze` object | Reference to the maze for wall checks |
| `mode` | BlueGhost only | `str` | `"scatter"` or `"chase"` |
| `mode_timer` | BlueGhost only | `float` | Seconds in current mode |

### Key Constants (from `constants.py`)

| Constant | Value | What It Does For Ghosts |
|---|---|---|
| `CELL_SIZE` | 20 | Size of each grid cell; used for all coordinate conversions |
| `MAZE_LEVEL_START_X` | -440.0 | Left edge of the maze in pixel coordinates |
| `MAZE_LEVEL_START_Y` | 250.0 | Top edge of the maze in pixel coordinates |
| `PLAYER_MOVE_SPEED` | 4 | Pac-Man's speed (ghosts start slower and get faster) |

### Pathfinding Algorithm Summary

| Algorithm | Function | Cost per Step | Guarantees Shortest? | Used By |
|---|---|---|---|---|
| Breadth-First Search | `bfs()` | Uniform (1 per step) | YES (fewest steps) | Red Ghost |
| Depth-First Search | `dfs()` | Uniform (1 per step) | NO | Yellow Ghost |
| Uniform Cost Search | `ucs()` | Cardinal = 1.0, Diagonal = 1.414 | YES (lowest total cost) | Blue Ghost |
| Minimax | `minimax_neighbor_to()` | Evaluates position quality, not path length | N/A (looks ahead) | Green Ghost |

### Key Functions and Where to Find Them

| Function | File | What It Does |
|---|---|---|
| `BaseGhost.move()` | actors.py | Per-frame update: scale speed/size, move toward target, decide next target |
| `BaseGhost.choose_next_target()` | actors.py | Get neighbors, filter reverse, delegate to ghost-specific AI |
| `BaseGhost.get_neighbors()` | actors.py | Find all 8-direction cells reachable via `can_step_grid` |
| `BaseGhost.path_neighbor_to()` | actors.py | Run BFS, return first step of shortest path (for Red) |
| `BaseGhost.dfs_neighbor_to()` | actors.py | Run DFS, return first step of any path (for Yellow) |
| `BaseGhost.ucs_neighbor_to()` | actors.py | Run UCS, return first step of cheapest path (for Blue) |
| `BaseGhost.minimax_neighbor_to()` | actors.py | 3-ply minimax search (for Green) |
| `BaseGhost.closest_neighbor_to()` | actors.py | Greedy: pick neighbor with shortest `octile_distance` to target (fallback) |
| `BlueGhost.update_mode()` | actors.py | Timer-based scatter↔chase switching |
| `can_step_grid()` | actors.py | Check if move is legal, including diagonal corner-squeeze prevention |
| `is_open_cell()` | actors.py | Check if cell is not a wall (with wrapping) |
| `wrap_cell()` | actors.py | Wrap grid coordinates modulo grid size |
| `get_closest_valid_cell()` | actors.py | Failsafe: find nearest non-wall cell to a target |

---

*End of ghost_logic.md — you now know everything about how ghosts work in this codebase.*
