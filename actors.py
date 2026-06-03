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
            
            if new_dir in ["up", "down"]:
                col_float = (x - MAZE_LEVEL_START_X) / CELL_SIZE
                nearest_col = round(col_float)
                center_x = MAZE_LEVEL_START_X + CELL_SIZE * nearest_col
                
                if abs(x - center_x) <= TURN_TOLERANCE:
                    if new_dir == "up":
                        next_y = y + self.move_speed
                        if not (self.maze.is_wall(center_x - half_size, next_y + half_size) or
                                self.maze.is_wall(center_x + half_size, next_y + half_size)):
                            can_turn = True
                            snap_x = center_x
                    else: 
                        next_y = y - self.move_speed
                        if not (self.maze.is_wall(center_x - half_size, next_y - half_size) or
                                self.maze.is_wall(center_x + half_size, next_y - half_size)):
                            can_turn = True
                            snap_x = center_x
            else: 
                row_float = (MAZE_LEVEL_START_Y - y) / CELL_SIZE
                nearest_row = round(row_float)
                center_y = MAZE_LEVEL_START_Y - CELL_SIZE * nearest_row
                
                if abs(y - center_y) <= TURN_TOLERANCE:
                    if new_dir == "left":
                        next_x = x - self.move_speed
                        if not (self.maze.is_wall(next_x - half_size, center_y - half_size) or
                                self.maze.is_wall(next_x - half_size, center_y + half_size)):
                            can_turn = True
                            snap_y = center_y
                    else: 
                        next_x = x + self.move_speed
                        if not (self.maze.is_wall(next_x + half_size, center_y - half_size) or
                                self.maze.is_wall(next_x + half_size, center_y + half_size)):
                            can_turn = True
                            snap_y = center_y
            
            if can_turn:
                self.direction = new_dir
                if snap_x != x: 
                    self.setx(snap_x)
                    x = snap_x
                if snap_y != y: 
                    self.sety(snap_y)
                    y = snap_y
                self.buffered_direction = None
                self.buffer_timer = 0
            else:
                self.buffer_timer -= 1
                if self.buffer_timer <= 0:
                    self.buffered_direction = None

        if self.direction == "stop":
            return

        if self.direction == "up":
            next_y = y + self.move_speed
            if not (self.maze.is_wall(x - half_size, next_y + half_size) or
                    self.maze.is_wall(x + half_size, next_y + half_size)):
                self.sety(next_y)
            else:
                self.direction = "stop"
        elif self.direction == "down":
            next_y = y - self.move_speed
            if not (self.maze.is_wall(x - half_size, next_y - half_size) or
                    self.maze.is_wall(x + half_size, next_y - half_size)):
                self.sety(next_y)
            else:
                self.direction = "stop"
        elif self.direction == "left":
            next_x = x - self.move_speed
            if not (self.maze.is_wall(next_x - half_size, y - half_size) or
                    self.maze.is_wall(next_x - half_size, y + half_size)):
                self.setx(next_x)
            else:
                self.direction = "stop"
        elif self.direction == "right":
            next_x = x + self.move_speed
            if not (self.maze.is_wall(next_x + half_size, y - half_size) or
                    self.maze.is_wall(next_x + half_size, y + half_size)):
                self.setx(next_x)
            else:
                self.direction = "stop"

        if round(self.ycor()) > SCREEN_HEIGHT / 2 - 2 * CELL_SIZE:
            self.sety(-SCREEN_HEIGHT / 2)
        elif round(self.ycor()) < -SCREEN_HEIGHT / 2:
            self.sety(SCREEN_HEIGHT / 2 - 2 * CELL_SIZE)
        elif round(self.xcor()) < -SCREEN_WIDTH / 2:
            self.setx(SCREEN_WIDTH / 2)
        elif round(self.xcor()) > SCREEN_WIDTH / 2:
            self.setx(-SCREEN_WIDTH / 2)

    def reset_speed(self) -> None:
        self.move_speed = PLAYER_MOVE_SPEED       