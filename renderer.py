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
        self.pencolor("white")
        # Draw a box on the right from x = 230 to 450, y = -260 to 260
        self.goto(230, 260)
        self.pendown()
        self.goto(450, 260)
        self.goto(450, -260)
        self.goto(230, -260)
        self.goto(230, 260)
        self.penup()

    def draw_title_and_legend(self) -> None:
        # 1. Main Title (Two lines)
        self.goto(340, 210)
        self.pencolor("yellow")
        self.write("PAC-MAN", align="center", font=("Courier", 20, "bold"))
        self.goto(340, 180)
        self.write("EVOLUTION", align="center", font=("Courier", 20, "bold"))
        
        # 2. Ghost Logic Header
        self.goto(340, -60)
        self.pencolor("white")
        self.write("GHOST LOGIC", align="center", font=("Courier", 12, "bold"))
        
        # 3. Ghost Legend List (Vertical)
        ghosts_data = [
            ("RED", "red", "= Random", -100),
            ("ORANGE", "orange", "= Chase", -130),
            ("GREEN", "medium spring green", "= Ambush/Minimax", -160),
            ("CYAN", "cyan", "= UCS", -190)
        ]
        for name, color, logic, y in ghosts_data:
            self.goto(250, y)
            self.pencolor(color)
            self.write(name, align="left", font=("Courier", 10, "bold"))
            # Calculate spacing for inline logic label
            x_offset = 250 + len(name) * 8.5
            self.goto(x_offset, y)
            self.pencolor("white")
            self.write(logic, align="left", font=("Courier", 10, "bold"))

    def write_score(self, score) -> None:
        self.clear()
        self.pencolor("white")
        self.goto(340, 110)
        self.write("Live Score", align="center", font=self.font)
        self.goto(340, 80)
        self.write(f"{score}", align="center", font=("Courier", 20, "bold"))

    def write_lives(self, lives) -> None:
        self.clear()
        self.pencolor("white")
        self.goto(340, 20)
        self.write("Remaining Lives", align="center", font=self.font)
        self.goto(340, -10)
        self.write(f"{lives}", align="center", font=("Courier", 20, "bold"))
