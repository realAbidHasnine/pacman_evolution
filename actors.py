import turtle
from collections import deque
import heapq
from constants import (CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
                       PLAYER_MOVE_SPEED, MAZE_LEVEL_START_X,
                       MAZE_LEVEL_START_Y, MAZE_GRID_ROWS,
                       MAZE_GRID_COLUMNS)

DIRECTION_VECTORS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
    "up-left": (-1, -1),
    "up-right": (1, -1),
    "down-left": (-1, 1),
    "down-right": (1, 1),
}

CARDINAL_STEPS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL_STEPS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
EIGHT_WAY_STEPS = CARDINAL_STEPS + DIAGONAL_STEPS


def wrap_cell(gx, gy, grid):
    rows = len(grid)
    cols = len(grid[0])
    return (gx + cols) % cols, (gy + rows) % rows


def is_open_cell(gx, gy, grid):
    wx, wy = wrap_cell(gx, gy, grid)
    return grid[wy][wx] != "X"


def can_step_grid(gx, gy, dx, dy, grid):
    nx = gx + dx
    ny = gy + dy
    if not is_open_cell(nx, ny, grid):
        return False

    if dx != 0 and dy != 0:
        # Diagonal movement should not squeeze through two wall corners.
        return is_open_cell(gx + dx, gy, grid) and is_open_cell(gx, gy + dy, grid)

    return True


def octile_distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy)


def direction_to_delta(direction):
    return DIRECTION_VECTORS.get(direction, (0, 0))

class Actor(turtle.Turtle):
    def __init__(self) -> None:
        super().__init__()
        self.hideturtle()
        self.penup()
        self.speed(0)
    def get_heading(self) -> int:
        return round(self.heading()) 


class Player(Actor):
    def __init__(self, maze) -> None:
        super().__init__()
        self.showturtle()
        self.shape("circle")
        self.shapesize(0.9)
        self.pencolor("white")
        self.fillcolor("yellow")
        self.direction = "stop"
        self.move_speed = PLAYER_MOVE_SPEED
        self.lives = 3
        self.score = 0
        self.maze = maze
        
        self.buffered_direction = None
        self.buffer_timer = 0

    def queue_direction(self, direction: str) -> None:
        from constants import BUFFER_FRAMES
        self.buffered_direction = direction
        self.buffer_timer = BUFFER_FRAMES

    def reset_speed(self) -> None:
        from constants import PLAYER_MOVE_SPEED
        self.move_speed = PLAYER_MOVE_SPEED

    def move(self) -> None:
        x, y = self.xcor(), self.ycor()
        from constants import CELL_SIZE, MAZE_LEVEL_START_X, MAZE_LEVEL_START_Y, TURN_TOLERANCE
        
        half_size = CELL_SIZE * 0.45

        if self.buffered_direction:
            new_dir = self.buffered_direction
            can_turn = False
            snap_x, snap_y = x, y
            
            # Check if player is near a cell center to turn
            col_float = (x - MAZE_LEVEL_START_X) / CELL_SIZE
            row_float = (MAZE_LEVEL_START_Y - y) / CELL_SIZE
            is_at_center_x = abs(x - (MAZE_LEVEL_START_X + round(col_float) * CELL_SIZE)) <= TURN_TOLERANCE
            is_at_center_y = abs(y - (MAZE_LEVEL_START_Y - round(row_float) * CELL_SIZE)) <= TURN_TOLERANCE

            if is_at_center_x and is_at_center_y:
                center_x = MAZE_LEVEL_START_X + round(col_float) * CELL_SIZE
                center_y = MAZE_LEVEL_START_Y - round(row_float) * CELL_SIZE
                center_gx = round(col_float)
                center_gy = round(row_float)
                dir_dx, dir_dy = direction_to_delta(new_dir)

                can_turn = can_step_grid(center_gx, center_gy, dir_dx, dir_dy, self.maze.grid)
                snap_x, snap_y = center_x, center_y

            if can_turn:
                self.direction = new_dir
                if snap_x != x: self.setx(snap_x)
                if snap_y != y: self.sety(snap_y)
                x, y = snap_x, snap_y
                self.buffered_direction = None
            else:
                self.buffer_timer -= 1
                if self.buffer_timer <= 0:
                    self.buffered_direction = None

        if self.direction == "stop":
            return

        move_dist = self.move_speed
        next_x, next_y = x, y

        if "up" in self.direction:
            next_y += move_dist if "left" not in self.direction and "right" not in self.direction else move_dist * 0.707
        if "down" in self.direction:
            next_y -= move_dist if "left" not in self.direction and "right" not in self.direction else move_dist * 0.707
        if "left" in self.direction:
            next_x -= move_dist if "up" not in self.direction and "down" not in self.direction else move_dist * 0.707
        if "right" in self.direction:
            next_x += move_dist if "up" not in self.direction and "down" not in self.direction else move_dist * 0.707
        
        # Collision detection with sliding
        final_x = x
        final_y = y
        
        hitbox = half_size * 0.8
        
        if next_x != x:
            if next_x > x:
                if not (self.maze.is_wall(next_x + half_size, y + hitbox) or self.maze.is_wall(next_x + half_size, y - hitbox)):
                    final_x = next_x
            else:
                if not (self.maze.is_wall(next_x - half_size, y + hitbox) or self.maze.is_wall(next_x - half_size, y - hitbox)):
                    final_x = next_x
                    
        if next_y != y:
            if next_y > y:
                if not (self.maze.is_wall(final_x - hitbox, next_y + half_size) or self.maze.is_wall(final_x + hitbox, next_y + half_size)):
                    final_y = next_y
            else:
                if not (self.maze.is_wall(final_x - hitbox, next_y - half_size) or self.maze.is_wall(final_x + hitbox, next_y - half_size)):
                    final_y = next_y

        if final_x == x and final_y == y:
            self.direction = "stop"
        else:
            self.goto(final_x, final_y)

        # Screen wrapping
        left_limit = MAZE_LEVEL_START_X - CELL_SIZE / 2
        right_limit = MAZE_LEVEL_START_X + len(self.maze.grid[0]) * CELL_SIZE - CELL_SIZE / 2
        top_limit = MAZE_LEVEL_START_Y + CELL_SIZE / 2
        bottom_limit = MAZE_LEVEL_START_Y - len(self.maze.grid) * CELL_SIZE + CELL_SIZE / 2

        if self.xcor() > right_limit:
            self.setx(left_limit)
        elif self.xcor() < left_limit:
            self.setx(right_limit)

        if self.ycor() > top_limit:
            self.sety(bottom_limit)
        elif self.ycor() < bottom_limit:
            self.sety(top_limit)

    def reset_speed(self) -> None:
        self.move_speed = PLAYER_MOVE_SPEED


def bfs(start, target, grid):
    rows = len(grid)
    cols = len(grid[0])
    start = wrap_cell(start[0], start[1], grid)
    target = wrap_cell(target[0], target[1], grid)
    queue = deque([start])
    parent = {start: None}

    if start == target:
        return []

    found = False
    while queue:
        current = queue.popleft()
        if current == target:
            found = True
            break

        gx, gy = current
        for dx, dy in EIGHT_WAY_STEPS:
            nx = gx + dx
            ny = gy + dy

            if can_step_grid(gx, gy, dx, dy, grid):
                neighbor = ((nx + cols) % cols, (ny + rows) % rows)
                if neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)

    if not found:
        return []

    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path[1:]


def dfs(start, target, grid):
    rows = len(grid)
    cols = len(grid[0])
    start = wrap_cell(start[0], start[1], grid)
    target = wrap_cell(target[0], target[1], grid)
    stack = [start]
    parent = {start: None}

    if start == target:
        return []

    found = False
    while stack:
        current = stack.pop()
        if current == target:
            found = True
            break

        gx, gy = current
        for dx, dy in reversed(EIGHT_WAY_STEPS):
            if can_step_grid(gx, gy, dx, dy, grid):
                neighbor = ((gx + dx + cols) % cols, (gy + dy + rows) % rows)
                if neighbor not in parent:
                    parent[neighbor] = current
                    stack.append(neighbor)

    if not found:
        return []

    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path[1:]


def step_cost(dx, dy):
    return 1.414 if dx != 0 and dy != 0 else 1.0


def ucs(start, target, grid):
    rows = len(grid)
    cols = len(grid[0])
    start = wrap_cell(start[0], start[1], grid)
    target = wrap_cell(target[0], target[1], grid)
    frontier = [(0.0, start)]
    parent = {start: None}
    cost_so_far = {start: 0.0}

    if start == target:
        return []

    found = False
    while frontier:
        current_cost, current = heapq.heappop(frontier)
        if current_cost > cost_so_far[current]:
            continue
        if current == target:
            found = True
            break

        gx, gy = current
        for dx, dy in EIGHT_WAY_STEPS:
            if can_step_grid(gx, gy, dx, dy, grid):
                neighbor = ((gx + dx + cols) % cols, (gy + dy + rows) % rows)
                new_cost = current_cost + step_cost(dx, dy)
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    parent[neighbor] = current
                    heapq.heappush(frontier, (new_cost, neighbor))

    if not found:
        return []

    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path[1:]


def get_closest_valid_cell(target, grid):
    target_gx, target_gy = target
    rows = len(grid)
    cols = len(grid[0])

    target_gx, target_gy = wrap_cell(target_gx, target_gy, grid)

    if is_open_cell(target_gx, target_gy, grid):
        return (target_gx, target_gy)

    # BFS to find the closest valid cell
    queue = deque([(target_gx, target_gy)])
    visited = {(target_gx, target_gy)}

    while queue:
        gx, gy = queue.popleft()
        if is_open_cell(gx, gy, grid):
            return (gx, gy)

        for dx, dy in EIGHT_WAY_STEPS:
            nx = (gx + dx + cols) % cols
            ny = (gy + dy + rows) % rows
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
                
    return (1, 1)


class BaseGhost(Actor):
    def __init__(self, maze, color, start_gx, start_gy):
        super().__init__()
        self.showturtle()
        self.shape("square")
        self.shapesize(0.9)
        self.pencolor("white")
        self.fillcolor(color)
        self.maze = maze
        
        self.start_gx = start_gx
        self.start_gy = start_gy
        
        self.gx = start_gx
        self.gy = start_gy
        
        target_x, target_y = self.grid_to_world(self.gx, self.gy)
        self.goto(target_x, target_y)
        self.target_x = target_x
        self.target_y = target_y
        
        self.next_gx = start_gx
        self.next_gy = start_gy
        
    def grid_to_world(self, gx, gy):
        x = MAZE_LEVEL_START_X + gx * CELL_SIZE
        y = MAZE_LEVEL_START_Y - gy * CELL_SIZE
        return x, y
        
    def world_to_grid(self, x, y):
        gx = int((x - MAZE_LEVEL_START_X + CELL_SIZE // 2) / CELL_SIZE)
        gy = int((MAZE_LEVEL_START_Y - y + CELL_SIZE // 2) / CELL_SIZE)
        return gx, gy
        
    def handle_wrapping(self):
        grid_rows = len(self.maze.grid)
        grid_cols = len(self.maze.grid[0])
        
        if self.gx < 0:
            self.gx = grid_cols - 1
            tx, ty = self.grid_to_world(self.gx, self.gy)
            self.goto(tx, ty)
        elif self.gx >= grid_cols:
            self.gx = 0
            tx, ty = self.grid_to_world(self.gx, self.gy)
            self.goto(tx, ty)
            
        if self.gy < 0:
            self.gy = grid_rows - 1
            tx, ty = self.grid_to_world(self.gx, self.gy)
            self.goto(tx, ty)
        elif self.gy >= grid_rows:
            self.gy = 0
            tx, ty = self.grid_to_world(self.gx, self.gy)
            self.goto(tx, ty)
            
    def get_neighbors(self, gx, gy):
        neighbors = []
        for dx, dy in EIGHT_WAY_STEPS:
            nx = gx + dx
            ny = gy + dy

            if can_step_grid(gx, gy, dx, dy, self.maze.grid):
                neighbors.append((nx, ny))
        return neighbors
        
    def choose_next_target(self, player_x, player_y, player_dir, remaining_pellets):
        rows = len(self.maze.grid)
        cols = len(self.maze.grid[0])
        neighbors = self.get_neighbors(self.gx, self.gy)
        
        # Prevent 180-degree turns
        if len(neighbors) > 1 and hasattr(self, "prev_gx") and hasattr(self, "prev_gy"):
            prev_wrap_x = (self.prev_gx + cols) % cols
            prev_wrap_y = (self.prev_gy + rows) % rows
            filtered = []
            for nx, ny in neighbors:
                wrap_nx = (nx + cols) % cols
                wrap_ny = (ny + rows) % rows
                if (wrap_nx, wrap_ny) != (prev_wrap_x, prev_wrap_y):
                    filtered.append((nx, ny))
            if filtered:
                neighbors = filtered
                
        if not neighbors:
            neighbors = [(self.gx, self.gy)]
            
        self.prev_gx = self.gx
        self.prev_gy = self.gy
        
        best_neighbor = self.get_best_neighbor(neighbors, player_x, player_y, player_dir, remaining_pellets)
        self.next_gx, self.next_gy = best_neighbor

    def closest_neighbor_to(self, neighbors, target_cell):
        target_cell = get_closest_valid_cell(target_cell, self.maze.grid)

        best_neighbor = neighbors[0]
        best_score = float("inf")
        for nx, ny in neighbors:
            neighbor_cell = wrap_cell(nx, ny, self.maze.grid)
            score = octile_distance(neighbor_cell, target_cell)
            if score < best_score:
                best_score = score
                best_neighbor = (nx, ny)
        return best_neighbor

    def path_neighbor_to(self, neighbors, target_cell):
        target_cell = get_closest_valid_cell(target_cell, self.maze.grid)
        start_cell = wrap_cell(self.gx, self.gy, self.maze.grid)
        path = bfs(start_cell, target_cell, self.maze.grid)

        if path:
            next_step = path[0]
            for nx, ny in neighbors:
                if wrap_cell(nx, ny, self.maze.grid) == next_step:
                    return (nx, ny)

        return self.closest_neighbor_to(neighbors, target_cell)

    def dfs_neighbor_to(self, neighbors, target_cell):
        target_cell = get_closest_valid_cell(target_cell, self.maze.grid)
        start_cell = wrap_cell(self.gx, self.gy, self.maze.grid)
        path = dfs(start_cell, target_cell, self.maze.grid)

        if path:
            next_step = path[0]
            for nx, ny in neighbors:
                if wrap_cell(nx, ny, self.maze.grid) == next_step:
                    return (nx, ny)

        return self.closest_neighbor_to(neighbors, target_cell)

    def ucs_neighbor_to(self, neighbors, target_cell):
        target_cell = get_closest_valid_cell(target_cell, self.maze.grid)
        start_cell = wrap_cell(self.gx, self.gy, self.maze.grid)
        path = ucs(start_cell, target_cell, self.maze.grid)

        if path:
            next_step = path[0]
            for nx, ny in neighbors:
                if wrap_cell(nx, ny, self.maze.grid) == next_step:
                    return (nx, ny)

        return self.closest_neighbor_to(neighbors, target_cell)

    def minimax_neighbor_to(self, neighbors, player_cell, depth=3):
        grid = self.maze.grid
        player_cell = get_closest_valid_cell(player_cell, grid)

        def legal_steps(cell):
            gx, gy = cell
            steps = []
            for dx, dy in EIGHT_WAY_STEPS:
                if can_step_grid(gx, gy, dx, dy, grid):
                    steps.append(wrap_cell(gx + dx, gy + dy, grid))
            return steps or [wrap_cell(gx, gy, grid)]

        def score_position(ghost_cell, pac_cell):
            distance_score = -octile_distance(ghost_cell, pac_cell)
            escape_routes = len(legal_steps(pac_cell))
            return distance_score - escape_routes * 0.35

        def search(ghost_cell, pac_cell, remaining_depth, ghost_turn):
            if remaining_depth == 0 or ghost_cell == pac_cell:
                return score_position(ghost_cell, pac_cell)

            if ghost_turn:
                return max(
                    search(next_ghost, pac_cell, remaining_depth - 1, False)
                    for next_ghost in legal_steps(ghost_cell)
                )

            return min(
                search(ghost_cell, next_pac, remaining_depth - 1, True)
                for next_pac in legal_steps(pac_cell)
            )

        best_neighbor = neighbors[0]
        best_score = float("-inf")
        for nx, ny in neighbors:
            ghost_cell = wrap_cell(nx, ny, grid)
            score = search(ghost_cell, player_cell, depth - 1, False)
            if score > best_score:
                best_score = score
                best_neighbor = (nx, ny)

        return best_neighbor
        
    def move(self, player_x, player_y, player_dir, remaining_pellets, total_pellets):
        fraction_eaten = 0.0
        if total_pellets > 0:
            fraction_eaten = (total_pellets - remaining_pellets) / total_pellets
            
        # Scale speed and size based on game progress (pellets eaten)
        self.move_speed = self.base_speed + fraction_eaten * 2.7
        self.shapesize(0.9 + fraction_eaten * 0.3)
        
        if hasattr(self, "update_mode"):
            self.update_mode(1/60, fraction_eaten)
            
        x, y = self.xcor(), self.ycor()
        dist = ((self.target_x - x)**2 + (self.target_y - y)**2)**0.5
        
        if dist < self.move_speed:
            self.goto(self.target_x, self.target_y)
            self.gx = self.next_gx
            self.gy = self.next_gy
            self.handle_wrapping()
            self.choose_next_target(player_x, player_y, player_dir, remaining_pellets)
            self.target_x, self.target_y = self.grid_to_world(self.next_gx, self.next_gy)
            
        # Re-fetch coordinates and move towards target
        x, y = self.xcor(), self.ycor()
        dx = self.target_x - x
        dy = self.target_y - y
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            step = min(self.move_speed, dist)
            step_x = (dx / dist) * step
            step_y = (dy / dist) * step
            self.goto(x + step_x, y + step_y)


class RedGhost(BaseGhost):
    def __init__(self, maze, start_gx, start_gy):
        super().__init__(maze, "red", start_gx, start_gy)
        self.base_speed = 2.0

    def get_best_neighbor(self, neighbors, player_x, player_y, player_dir, remaining_pellets):
        pgx, pgy = self.world_to_grid(player_x, player_y)
        return self.path_neighbor_to(neighbors, (pgx, pgy))


class YellowGhost(BaseGhost):
    def __init__(self, maze, start_gx, start_gy):
        super().__init__(maze, "yellow", start_gx, start_gy)
        self.base_speed = 2.2
        
    def get_best_neighbor(self, neighbors, player_x, player_y, player_dir, remaining_pellets):
        pgx, pgy = self.world_to_grid(player_x, player_y)
        return self.dfs_neighbor_to(neighbors, (pgx, pgy))


class GreenGhost(BaseGhost):
    def __init__(self, maze, start_gx, start_gy):
        super().__init__(maze, "green", start_gx, start_gy)
        self.base_speed = 2.1
        
    def get_best_neighbor(self, neighbors, player_x, player_y, player_dir, remaining_pellets):
        pgx, pgy = self.world_to_grid(player_x, player_y)
        return self.minimax_neighbor_to(neighbors, (pgx, pgy))


class BlueGhost(BaseGhost):
    def __init__(self, maze, start_gx, start_gy):
        super().__init__(maze, "blue", start_gx, start_gy)
        self.base_speed = 2.3
        self.mode_timer = 0.0
        self.mode = "scatter"
        
    def update_mode(self, dt, fraction_eaten):
        scatter_duration = max(1.0, 7.0 - fraction_eaten * 6.0)
        chase_duration = 20.0
        
        self.mode_timer += dt
        if self.mode == "scatter":
            if self.mode_timer >= scatter_duration:
                self.mode = "chase"
                self.mode_timer = 0.0
        else:
            if self.mode_timer >= chase_duration:
                self.mode = "scatter"
                self.mode_timer = 0.0
                
    def get_best_neighbor(self, neighbors, player_x, player_y, player_dir, remaining_pellets):
        cols = len(self.maze.grid[0])
        rows = len(self.maze.grid)

        if self.mode == "scatter":
            target_cell = (cols - 2, rows - 2)
        else:
            pgx, pgy = self.world_to_grid(player_x, player_y)
            dx, dy = direction_to_delta(player_dir)
            if dx == 0 and dy == 0:
                target_cell = (pgx, pgy)
            else:
                left_flank = (-dy, dx)
                right_flank = (dy, -dx)
                left_target = (pgx + left_flank[0] * 4, pgy + left_flank[1] * 4)
                right_target = (pgx + right_flank[0] * 4, pgy + right_flank[1] * 4)

                ghost_cell = wrap_cell(self.gx, self.gy, self.maze.grid)
                left_score = octile_distance(ghost_cell, wrap_cell(left_target[0], left_target[1], self.maze.grid))
                right_score = octile_distance(ghost_cell, wrap_cell(right_target[0], right_target[1], self.maze.grid))
                target_cell = left_target if left_score >= right_score else right_target

        return self.ucs_neighbor_to(neighbors, target_cell)
