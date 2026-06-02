"""
Pac-Man Evolution - Maze Data
X = Wall
. = Pellet
O = Power Pellet
"""

from constants import (CELL_SIZE, MAZE_GRID_ROWS, MAZE_GRID_COLUMNS,
                       MAZE_LEVEL_START_X, MAZE_LEVEL_START_Y)


maze_level_1 = [
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX",
    "X..............................OX",
    "X.XXX.XXX.XXXXXX.XXXXXX.XXX.XXX.X",
    "X.X X.X X.X    X.X    X.X X.X X.X",
    "X.XXX.X X.XXXXXX.XXXXXX.X X.XXX.X",
    "X.....XXX.X....X.X....X.XXX.....X",
    "XXXXX.......XX.X.X.XX.......XXXXX",
    "X.....XXXXX...........XXXXX.....X",
    "X.XXX.......XXXXXXXXX.......XXX.X",
    "X.....XXXXX...........XXXXX.....X",
    "X.XXX...O...XXXX.XXXX.......XXX.X",
    "X.X X.XXXXX.X  X.X  X.XXXXX.X X.X",
    "X.X X.X   X.X  X.X  X.X   X.X X.X",
    "X.X X.X   X.X  X.X  X.X   X.X X.X",
    "X.X X.XXXXX.X  X.X  X.XXXXX.X X.X",
    "X.XXX.......XXXX.XXXX...O...XXX.X",
    "X.....XXXXX...........XXXXX.....X",
    "X.XXX.......XXXXXXXXX.......XXX.X",
    "X.....XXXXX...........XXXXX.....X",
    "XXXXX.......XX.X.X.XX.......XXXXX",
    "X.....XXX.X....X.X....X.XXX.....X",
    "X.XXX.X X.XXXXXX.XXXXXX.X X.XXX.X",
    "X.X X.X X.X    X.X    X.X X.X X.X",
    "X.XXX.XXX.XXXXXX.XXXXXX.XXX.XXX.X",
    "XO..............................X",
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX"
]


def calculate_maze_data(maze_level):
    "Calculate maze coordinates"
    walls = []
    pellets = []
    power_pellets = []
    for row in range(MAZE_GRID_ROWS):
        for column in range(MAZE_GRID_COLUMNS):
            character = maze_level[row][column]
            character_x = MAZE_LEVEL_START_X + CELL_SIZE * column
            character_y = MAZE_LEVEL_START_Y - CELL_SIZE * row
            if character == "X":
                walls.append((character_x, character_y))
            elif character == ".":
                pellets.append((character_x, character_y))
            elif character == "O":
                power_pellets.append((character_x, character_y))
    return walls, pellets, power_pellets