import turtle
from turtle import _Screen

def init_screen():
    """Initialize main Screen"""

    screen = turtle.Screen()
    screen.tracer(0)
    screen.title("PacMan Evolution")
    screen.setup(width=1000, height=800)
    screen.bgcolor("black")

    return screen

def game_loop(screen) -> None:
    screen.update()

def main() -> None:
    screen: _Screen = init_screen()
    game_loop(screen)
    screen.mainloop()

if __name__ =="__main__":
    main()        