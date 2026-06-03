import turtle
from mazes import maze_level_1, get_maze
from constants import CELL_SIZE, SCREEN_HEIGHT , SCREEN_WIDTH


class Pen(turtle.Turtle):
    """Pen class to draw the maze"""

    def __init__(self, maze):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.color("silver")
        self.speed(0)
        self.maze = maze

class Wall(Pen):
    """Wall class to draw the walls of the maze"""

    def __init__(self, maze) -> None:
        super().__init__(maze)
        self.shape("square")
        self.shapesize(1.2)
        self.pencolor("white")
        self.fillcolor("dodger blue")

    def draw(self) -> None:
        """Draw the walls of the maze"""
        for x,y in self.maze.walls:
            self.goto(x, y)
            self.stamp()
class Pellet(Pen):
    """Pellet class to draw the pellets of the maze"""

    def __init__(self, maze) -> None:
        super().__init__(maze)
        self.shape("circle")
        self.shapesize(.35,.35)
        self.pencolor("white")
        self.fillcolor("gold")
        self.stamps = {}

    def draw(self) -> None:
        """Draw the pellets of the maze"""
        for x,y in self.maze.pellets:
            self.goto(x, y)
            stamp_id = self.stamp()
            self.stamps[(x,y)] = stamp_id
class PowerPellet(Pen):
    """PowerPellet class to draw the power pellets of the maze"""

    def __init__(self, maze) -> None:
        super().__init__(maze)
        self.shape("circle")
        self.shapesize(.8,.8)
        self.pencolor("white")
        self.fillcolor("chartreuse")
        self.stamps = {}

    def draw(self) -> None:
        """Draw the power pellets of the maze"""
        for x,y in self.maze.power_pellets:
            self.goto(x, y)
            stamp_id = self.stamp()
            self.stamps[(x,y)] = stamp_id

class UiPanel(Pen):
    """UiPanel class to draw the UI panel of the game"""

    def __init__(self) -> None:
        super().__init__(None)
        self.font = ("Courier", 30, "normal")

    def draw_ui_area(self) -> None:
        self.pensize(2)
        x = .9 * (SCREEN_WIDTH / 2)
        top_y = .98 * (SCREEN_HEIGHT / 2) 
        bottom_y = top_y - 1.5 * CELL_SIZE
        self.goto(x, top_y)
        self.pendown()
        self.goto(-x,top_y)
        self.goto(-x, bottom_y)
        self.goto(x, bottom_y)
        self.goto(x, top_y)

    def write_score(self, score) -> None:
        self.clear()
        self.goto(-SCREEN_WIDTH / 4, .98 * (SCREEN_HEIGHT / 2) - 1.2 * CELL_SIZE)
        self.write(f"Score: {score}", align="center", font=self.font)

    def write_lives(self, lives) -> None:
        self.clear()
        self.goto(SCREEN_WIDTH / 4, .98 * (SCREEN_HEIGHT / 2) - 1.2 * CELL_SIZE)
        self.write(f"Lives: {lives}", align="center", font=self.font)
