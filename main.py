import turtle
import random
from turtle import _Screen

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, MAZE_LEVEL_START_X, MAZE_LEVEL_START_Y
from renderer import Wall, Pellet, PowerPellet,UiPanel
from actors import Player, RedGhost, YellowGhost, GreenGhost, BlueGhost
from mazes import maze_level_1, get_maze


def init_screen():
    

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


def show_game_over(screen, ui_panel, restart_callback):
    ui_panel.goto(0, 0)
    ui_panel.pencolor("red")
    ui_panel.write("GAME OVER", align="center", font=("Courier", 40, "bold"))
    
    # Draw button background (white)
    ui_panel.goto(-80, -85)
    ui_panel.setheading(0)
    ui_panel.fillcolor("white")
    ui_panel.begin_fill()
    for _ in range(2):
        ui_panel.forward(160)
        ui_panel.left(90)
        ui_panel.forward(40)
        ui_panel.left(90)
    ui_panel.end_fill()

    # Draw Restart Button Text (black)
    ui_panel.goto(0, -75)
    ui_panel.pencolor("black")
    ui_panel.write("RESTART", align="center", font=("Courier", 20, "bold"))
    ui_panel.penup()
    
    def handle_click(x, y):
        # Button boundaries: x in [-80, 80], y in [-85, -45]
        if -80 <= x <= 80 and -85 <= y <= -45:
            screen.onclick(None)
            restart_callback()

    screen.onclick(handle_click)
    screen.update()


def show_victory(screen, ui_panel, restart_callback):
    ui_panel.goto(0, 0)
    ui_panel.pencolor("chartreuse")
    ui_panel.write("YOU WIN!", align="center", font=("Courier", 40, "bold"))
    
    # Draw button background (white)
    ui_panel.goto(-80, -85)
    ui_panel.setheading(0)
    ui_panel.fillcolor("white")
    ui_panel.begin_fill()
    for _ in range(2):
        ui_panel.forward(160)
        ui_panel.left(90)
        ui_panel.forward(40)
        ui_panel.left(90)
    ui_panel.end_fill()

    # Draw Restart Button Text (black)
    ui_panel.goto(0, -75)
    ui_panel.pencolor("black")
    ui_panel.write("RESTART", align="center", font=("Courier", 20, "bold"))
    ui_panel.penup()
    
    def handle_click(x, y):
        # Button boundaries: x in [-80, 80], y in [-85, -45]
        if -80 <= x <= 80 and -85 <= y <= -45:
            screen.onclick(None)
            restart_callback()

    screen.onclick(handle_click)
    screen.update()


def reset_positions(player, ghosts, player_start_x, player_start_y):
    player.goto(player_start_x, player_start_y)
    player.direction = "stop"
    player.buffered_direction = None
    
    for ghost in ghosts:
        start_x, start_y = ghost.grid_to_world(ghost.start_gx, ghost.start_gy)
        ghost.goto(start_x, start_y)
        ghost.gx = ghost.start_gx
        ghost.gy = ghost.start_gy
        ghost.next_gx = ghost.start_gx
        ghost.next_gy = ghost.start_gy
        ghost.target_x = start_x
        ghost.target_y = start_y
        if hasattr(ghost, "prev_gx"):
            del ghost.prev_gx
        if hasattr(ghost, "prev_gy"):
            del ghost.prev_gy


def game_loop(screen, player, ghosts, score_panel, lives_panel, ui_panel, pellet_pen, power_pellet_pen, player_start_x, player_start_y, total_pellets, restart_callback) -> None:
    score_panel.write_score(player.score)
    lives_panel.write_lives(player.lives)

    remaining_pellets = len(pellet_pen.stamps)
    
    if remaining_pellets == 0:
        show_victory(screen, ui_panel, restart_callback)
        return

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
    
    # Move ghosts and handle collisions
    for ghost in ghosts:
        ghost.move(player.xcor(), player.ycor(), player.direction, remaining_pellets, total_pellets)
        
        if player.distance(ghost) < CELL_SIZE * 0.8:
            player.lives -= 1
            if player.lives > 0:
                reset_positions(player, ghosts, player_start_x, player_start_y)
            else:
                show_game_over(screen, ui_panel, restart_callback)
                return

    screen.update()
    screen.ontimer(lambda: game_loop(screen, player, ghosts, score_panel, lives_panel, ui_panel, pellet_pen, power_pellet_pen, player_start_x, player_start_y, total_pellets, restart_callback), 1000 // 60)


def main() -> None:
    screen: _Screen = init_screen()

    maze = get_maze(maze_level_1)

    wall_pen: Wall = Wall(maze)
    pellet_pen: Pellet = Pellet(maze)
    power_pellet_pen: PowerPellet = PowerPellet(maze)

    ui_panel = UiPanel()
    score_panel = UiPanel()
    lives_panel = UiPanel()
    message_panel = UiPanel() # Separate panel for Game Over / Victory messages

    wall_pen.draw()
    ui_panel.draw_ui_area()
    ui_panel.draw_title_and_legend()

    player = Player(maze)

    # Filter player starting position so it doesn't spawn exactly on top of ghost spawn corners
    ghost_starts = [(1, 1), (31, 1), (1, 23), (31, 23)]
    ghost_start_world_coords = []
    for gx, gy in ghost_starts:
        x = MAZE_LEVEL_START_X + gx * CELL_SIZE
        y = MAZE_LEVEL_START_Y - gy * CELL_SIZE
        ghost_start_world_coords.append((x, y))

    candidate_starts = [
        coor for coor in maze.pellets
        if coor not in ghost_start_world_coords
    ]
    if not candidate_starts:
        candidate_starts = maze.pellets

    # Initialize the 4 ghosts
    red_ghost = RedGhost(maze, 1, 1)
    yellow_ghost = YellowGhost(maze, 31, 1)
    green_ghost = GreenGhost(maze, 1, 23)
    blue_ghost = BlueGhost(maze, 31, 23)
    ghosts = [red_ghost, yellow_ghost, green_ghost, blue_ghost]

    def start_new_game():
        # Clear any existing messages and reset UI panels
        message_panel.clear()
        score_panel.clear()
        lives_panel.clear()
        
        # Reset Pellets
        pellet_pen.clearstamps()
        pellet_pen.stamps = {}
        pellet_pen.draw()
        
        power_pellet_pen.clearstamps()
        power_pellet_pen.stamps = {}
        power_pellet_pen.draw()
        
        # Reset Player stats
        player.score = 0
        player.lives = 3
        player.reset_speed()
        
        # Reset positions
        player_start_coor = random.choice(candidate_starts)
        reset_positions(player, ghosts, player_start_coor[0], player_start_coor[1])
        
        # Ensure controls are bound and screen is listening
        bind_controls(screen, player)
        
        total_pellets = len(pellet_pen.stamps)

        game_loop(screen, player, ghosts, score_panel, lives_panel, message_panel, pellet_pen, power_pellet_pen, player_start_coor[0], player_start_coor[1], total_pellets, start_new_game)

    start_new_game()
    screen.mainloop()

# rdfgdgrdhdrt/

if __name__ == "__main__":
    main()        