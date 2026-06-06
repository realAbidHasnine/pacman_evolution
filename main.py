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
    pressed_keys = set()

    def update_direction():
        if "Up" in pressed_keys and "Left" in pressed_keys:
            player.queue_direction("up-left")
        elif "Up" in pressed_keys and "Right" in pressed_keys:
            player.queue_direction("up-right")
        elif "Down" in pressed_keys and "Left" in pressed_keys:
            player.queue_direction("down-left")
        elif "Down" in pressed_keys and "Right" in pressed_keys:
            player.queue_direction("down-right")
        elif "Up" in pressed_keys:
            player.queue_direction("up")
        elif "Down" in pressed_keys:
            player.queue_direction("down")
        elif "Left" in pressed_keys:
            player.queue_direction("left")
        elif "Right" in pressed_keys:
            player.queue_direction("right")

    def on_press(key):
        pressed_keys.add(key)
        update_direction()

    def on_release(key):
        pressed_keys.discard(key)
        update_direction()

    screen.listen()
    screen.onkeypress(lambda: on_press("Up"), "Up")
    screen.onkeyrelease(lambda: on_release("Up"), "Up")
    screen.onkeypress(lambda: on_press("Down"), "Down")
    screen.onkeyrelease(lambda: on_release("Down"), "Down")
    screen.onkeypress(lambda: on_press("Left"), "Left")
    screen.onkeyrelease(lambda: on_release("Left"), "Left")
    screen.onkeypress(lambda: on_press("Right"), "Right")
    screen.onkeyrelease(lambda: on_release("Right"), "Right")
    
    screen.onkeypress(lambda: player.queue_direction("up-left"), "q")
    screen.onkeypress(lambda: player.queue_direction("up-right"), "e")
    screen.onkeypress(lambda: player.queue_direction("down-left"), "z")
    screen.onkeypress(lambda: player.queue_direction("down-right"), "c")


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