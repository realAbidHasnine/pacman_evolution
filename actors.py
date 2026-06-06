import turtle
from constants import (CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
                       PLAYER_MOVE_SPEED, MAZE_LEVEL_START_X,
                       MAZE_LEVEL_START_Y, MAZE_GRID_ROWS,
                       MAZE_GRID_COLUMNS)

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
        self.shapesize(1.4)
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

                # Simplified check for turning, can be improved
                can_turn = True
                snap_x, snap_y = center_x, center_y

            if can_turn:
                self.direction = new_dir
                if snap_x != x: self.setx(snap_x)
                if snap_y != y: self.sety(snap_y)
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
        if self.xcor() > SCREEN_WIDTH / 2:
            self.setx(-SCREEN_WIDTH / 2)
        elif self.xcor() < -SCREEN_WIDTH / 2:
            self.setx(SCREEN_WIDTH / 2)
        if self.ycor() > SCREEN_HEIGHT / 2:
            self.sety(-SCREEN_HEIGHT / 2)
        elif self.ycor() < -SCREEN_HEIGHT / 2:
            self.sety(SCREEN_HEIGHT / 2)

    def reset_speed(self) -> None:
        self.move_speed = PLAYER_MOVE_SPEED       