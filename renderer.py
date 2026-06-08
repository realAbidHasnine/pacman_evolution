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
        self.shapesize(0.9)
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
        self.shapesize(.2,.2)
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
        self.shapesize(.5,.5)
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
        self.font = ("Courier", 14, "bold")

    def draw_ui_area(self) -> None:
        self.pensize(2)
        x = .9 * (SCREEN_WIDTH / 2)
        top_y = .98 * (SCREEN_HEIGHT / 2) 
        bottom_y = top_y - 3.2 * CELL_SIZE
        self.goto(x, top_y)
        self.pendown()
        self.goto(-x,top_y)
        self.goto(-x, bottom_y)
        self.goto(x, bottom_y)
        self.goto(x, top_y)
        self.penup()

    def draw_title_and_legend(self) -> None:
        # 1. Ghost Legend (horizontally distributed and colored)
        y_pos = .98 * (SCREEN_HEIGHT / 2) - 2.3 * CELL_SIZE
        
        self.goto(-320, y_pos)
        self.pencolor("white")
        self.write("Ghost Logic: ", align="left", font=("Courier", 10, "bold"))
        
        self.goto(-230, y_pos)
        self.pencolor("red")
        self.write("RED", align="left", font=("Courier", 10, "bold"))
        self.pencolor("white")
        self.goto(-205, y_pos)
        self.write("=Random  ", align="left", font=("Courier", 10, "bold"))
        
        self.goto(-140, y_pos)
        self.pencolor("orange")
        self.write("ORANGE", align="left", font=("Courier", 10, "bold"))
        self.pencolor("white")
        self.goto(-95, y_pos)
        self.write("=Chase  ", align="left", font=("Courier", 10, "bold"))
        
        self.goto(-35, y_pos)
        self.pencolor("medium spring green")
        self.write("GREEN", align="left", font=("Courier", 10, "bold"))
        self.pencolor("white")
        self.goto(5, y_pos)
        self.write("=Ambush  ", align="left", font=("Courier", 10, "bold"))
        
        self.goto(70, y_pos)
        self.pencolor("cyan")
        self.write("CYAN", align="left", font=("Courier", 10, "bold"))
        self.pencolor("white")
        self.goto(105, y_pos)
        self.write("=Scatter/Chase", align="left", font=("Courier", 10, "bold"))

    def write_score(self, score) -> None:
        self.clear()
        self.goto(-SCREEN_WIDTH / 4, .98 * (SCREEN_HEIGHT / 2) - 1.1 * CELL_SIZE)
        self.pencolor("white")
        self.write(f"Live Score: {score}", align="center", font=self.font)

    def write_lives(self, lives) -> None:
        self.clear()
        self.goto(SCREEN_WIDTH / 4, .98 * (SCREEN_HEIGHT / 2) - 1.1 * CELL_SIZE)
        self.pencolor("white")
        self.write(f"Remaining Lives: {lives}", align="center", font=self.font)
