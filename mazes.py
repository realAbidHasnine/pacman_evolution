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
    "X...............O...............X",
    "X.XXXX.XXXX.XXXX.XXXX.XXXX.XXXX.X",
    "X.XXXX.XXXX.XXXX.XXXX.XXXX.XXXX.X",
    "X...............................X",
    "X.XXXX.XXX.............XXX.XXXX.X",
    "X.XXXX.XXXX...........XXXX.XXXX.X",
    "X......XXXXX.........XXXXX......X",
    "XXXXXX.XXXXXX.......XXXXXX.XXXXXX",
    "XXXXXX.XXXXXXX.....XXXXXXX.XXXXXX",
    "XXXXXX.XXXXXXXX...XXXXXXXX.XXXXXX",
    "XXXXXX.XXXXXXXXX.XXXXXXXXX.XXXXXX",
    ".......XXXXXXXX...XXXXXXXX.......",
    "XXXXXX.XXXXXXX.....XXXXXXX.XXXXXX",
    "XXXXXX.XXXXXX.......XXXXXX.XXXXXX",
    "XXXXXX.XXXXX.........XXXXX.XXXXXX",
    "XXXXXX.XXXX...........XXXX.XXXXXX",
    "X......XXX.............XXX......X",
    "X.XXXX.XX...............XX.XXXX.X",
    "X.XXXX.X.................X.XXXX.X",
    "X...............O...............X",
    "X.XXXX.XXXX.XXXX.XXXX.XXXX.XXXX.X",
    "X.XXXX.XXXX.XXXX.XXXX.XXXX.XXXX.X",
    "X...............................X",
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX"
    
]


class Maze:
    def __init__(self, maze_level):
        self.grid = maze_level
        self.walls, self.pellets, self.power_pellets = self._calculate_maze_data()

    def _calculate_maze_data(self):
        walls = []
        pellets = []
        power_pellets = []
        for row in range(len(self.grid)):
            for column in range(len(self.grid[row])):
                character = self.grid[row][column]
                character_x = MAZE_LEVEL_START_X + CELL_SIZE * column
                character_y = MAZE_LEVEL_START_Y - CELL_SIZE * row
                if character == "X":
                    walls.append((character_x, character_y))
                elif character == ".":
                    pellets.append((character_x, character_y))
                elif character == "O":
                    power_pellets.append((character_x, character_y))
        return walls, pellets, power_pellets

    def is_wall(self, x, y):
        # Convert world coordinates to grid coordinates
        grid_x = int((x - MAZE_LEVEL_START_X + CELL_SIZE // 2) / CELL_SIZE)
        grid_y = int((MAZE_LEVEL_START_Y - y + CELL_SIZE // 2) / CELL_SIZE)

        # Check if the coordinates are within the grid boundaries
        if 0 <= grid_y < len(self.grid) and 0 <= grid_x < len(self.grid[0]):
            return self.grid[grid_y][grid_x] == "X"
        return False


def get_maze(level):
    return Maze(level)