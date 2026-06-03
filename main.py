import turtle
import random
from turtle import _Screen

from constants import SCREEN_WIDTH, SCREEN_HEIGHT,CELL_SIZE
from renderer import Wall, Pellet, PowerPellet,UiPanel
from actors import Player
from mazes import maze_level_1, get_maze


def init_screen():
    """Initialize main Screen"""

    screen = turtle.Screen()
    screen.tracer(0)
    screen.title("PacMan Evolution")
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.bgcolor("black")

    return screen


def bind_controls(screen, player) -> None:
    screen.listen()
    screen.onkeypress(lambda: player.queue_direction("up"), "Up")
    screen.onkeypress(lambda: player.queue_direction("down"), "Down")
    screen.onkeypress(lambda: player.queue_direction("left"), "Left")
    screen.onkeypress(lambda: player.queue_direction("right"), "Right")


def game_loop(screen, player,score_panel,lives_panel,pellet_pen,power_pellet_pen,player_start_x,player_start_y) -> None:
    score_panel.write_score(player.score)
    lives_panel.write_lives(player.lives)

    for (px,py),stamp_id in list(pellet_pen.stamps.items()):
        if player.distance(px,py) < CELL_SIZE / 2 and (px,py)!=(player_start_x,player_start_y):
            pellet_pen.clearstamp(stamp_id)
            del pellet_pen.stamps[(px,py)]
            player.score += 10
        elif player.distance(px,py) < CELL_SIZE / 2 and (px,py)==(player_start_x,player_start_y):
            pellet_pen.clearstamp(stamp_id)
            del pellet_pen.stamps[(px,py)]

    for (px,py),stamp_id in list(power_pellet_pen.stamps.items()):
        if player.distance(px,py) < CELL_SIZE / 2:
            power_pellet_pen.clearstamp(stamp_id)
            del power_pellet_pen.stamps[(px,py)]
            player.score += 50
            player.move_speed += 3
            screen.ontimer(player.reset_speed, 3000)
                


    player.move()
    screen.update()
    screen.ontimer(lambda: game_loop(screen, player,score_panel,lives_panel,pellet_pen,power_pellet_pen,player_start_x,player_start_y), 1000 // 60)


def main() -> None:
    screen: _Screen = init_screen()

    maze = get_maze(maze_level_1)

    wall_pen: Wall = Wall(maze)
    pellet_pen: Pellet = Pellet(maze)
    power_pellet_pen: PowerPellet = PowerPellet(maze)

    ui_panel = UiPanel()
    score_panel = UiPanel()
    lives_panel = UiPanel()

    wall_pen.draw()
    pellet_pen.draw()
    power_pellet_pen.draw()
    ui_panel.draw_ui_area()

    

    player = Player(maze)

    player_start_coor = random.choice(pellet_pen.maze.pellets)
    player.goto(player_start_coor[0], player_start_coor[1])
    bind_controls(screen, player)

    game_loop(screen, player,score_panel,lives_panel,pellet_pen,power_pellet_pen,player_start_coor[0],player_start_coor[1])
    screen.mainloop()


if __name__ == "__main__":
    main()        