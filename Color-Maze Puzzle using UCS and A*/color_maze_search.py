import sys
import time
from heapq import heappop, heappush
import queue
import copy
import os, psutil

# define the directions to explore adjacent cells
DIRECTIONS = [(-1, 0), (0, -1), (0, 1), (1, 0)]


# check if a given cell is within the bounds of the grid and is not a wall (i.e. is a valid cell to explore).
def is_valid(x, y, grid):
    return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != 'X'


def go_till_obstacle(grid, cell, direction):
    x, y = cell
    dx, dy = direction
    i = 1
    step = 0
    path = []
    while True:
        if is_valid(x + (dx * i), y + (dy * i), grid):
            path.append((x + (dx * i), y + (dy * i)))
            step += 1
            i += 1
        else:
            i -= 1
            break
    return step, (x + (dx * i), y + (dy * i)), path

def get_next_targets(grid, cell):
    x, y = cell

    # Check if there are uncolored cells adjacent to the current cell
    valid_neighbors = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny, grid) and grid[nx][ny] != 'X':
            valid_neighbors.append((nx, ny))

    if valid_neighbors:
        targets = []
        for nx, ny in valid_neighbors:
            step, pos, path_ = go_till_obstacle(grid, cell, (nx - x, ny - y))
            targets.append((step, pos, path_))
        return targets
    else:
        raise NotImplementedError

def total_uncolored(grid):
    return len([(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == '0'])

def all_visited(grid):
    if len([(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == '0']):
        return False
    else:
        return True
    
def paint_till_next_target(grid, path):
    for x, y in path:
        if grid[x][y] != 'S':
            grid[x][y] = "P"
    return grid

def ucs(grid, start):
    found_flag = False
    found_cost = sys.maxsize
    my_heap = []
    heappush(my_heap, (0, start, [start]))
    total_explored = 1
    
    while my_heap:
        curr_cost, curr_cell, curr_path = heappop(my_heap)
        
        painted_grid = copy.deepcopy(grid)
        painted_grid = paint_till_next_target(painted_grid, curr_path)

        if found_flag:
            if curr_cost >= found_cost:
                continue
        if total_uncolored(painted_grid) == 0:
            print(curr_cost, total_explored, curr_path)
            found_flag = True
            found_cost = curr_cost
            continue

        next_targets = get_next_targets(painted_grid, curr_cell)
        for each_target in next_targets:
            next_cost = curr_cost + each_target[0]

            next_path = curr_path.copy()

            for each in each_target[2]:
                next_path.append(each)

            heappush(my_heap, (next_cost, each_target[1], next_path ))
            total_explored += 1

def a_star(grid, start):
    found_flag = False
    found_f = sys.maxsize
    found_cost = sys.maxsize
    my_heap = []
    heappush(my_heap, (total_uncolored(grid), 0, start, [start]))
    total_explored = 1
    
    while my_heap:
        f, curr_cost, curr_cell, curr_path = heappop(my_heap)
        
        painted_grid = copy.deepcopy(grid)
        painted_grid = paint_till_next_target(painted_grid, curr_path)

        if found_flag:
            if curr_cost >= found_cost or f >= found_f:
                continue
        if total_uncolored(painted_grid) == 0:
            print(curr_cost, total_explored, curr_path)
            found_flag = True
            found_cost = curr_cost
            found_f = f
            continue

        next_targets = get_next_targets(painted_grid, curr_cell)
        for each_target in next_targets:

            next_path = copy.deepcopy(curr_path)

            for each in each_target[2]:
                next_path.append(each)

            next_grid = copy.deepcopy(painted_grid)
            next_grid = paint_till_next_target(next_grid, next_path)
            next_f = curr_cost + each_target[0] + total_uncolored(next_grid)

            heappush(my_heap, (next_f, curr_cost + each_target[0], each_target[1], next_path ))
            total_explored += 1

def solve_maze(grid, algorithm):
    # this loop finds the starting node denoted by an S
    start = None
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 'S':
                start = (i, j)

    # this loop finds the number of cells in the maze
    
    print("There are ", total_uncolored(grid) + 1, " cells in this maze")

    # solve the maze and print information
    start_time = time.time()
    if algorithm == "ucs":
        print("solving for UCS:")
        result = ucs(grid, start)
    else:
        print("solving for A* search:")
        result = a_star(grid, start)
    process = psutil.Process(os.getpid())
    print("the memory consumption is", process.memory_info().rss / 1024**(2), "MB") 
    print("the CPU time is %s seconds" % (time.time() - start_time))
    return result

# EASY 1
grid = [
    ["0","0","0","0","0","0","0","0","0","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["S","0","0","0","0","0","0","0","0","0"]
]

# # # EASY 2
# grid = [
#     ["X","X","X","X","S","X","X","X","X","X"],
#     ["X","X","X","X","0","X","X","X","X","X"],
#     ["X","X","X","X","0","X","X","X","X","X"],
#     ["X","X","X","X","0","X","X","X","X","X"],
#     ["0","0","0","0","0","0","0","0","0","0"],
#     ["0","X","X","X","0","X","X","X","X","0"],
#     ["0","X","X","X","0","X","X","X","X","0"],
#     ["0","X","X","X","0","X","X","X","X","0"],
#     ["0","X","X","X","0","X","X","X","X","0"],
#     ["0","0","0","0","0","X","X","X","X","0"]
# ]

# # EASY 3
# grid = [
#     ["0","X","0","0","0","0","0","0","0","X"],
#     ["0","X","0","X","X","X","X","X","0","X"],
#     ["0","X","0","X","0","0","0","0","0","X"],
#     ["0","X","0","X","0","X","X","X","X","X"],
#     ["0","X","0","X","0","0","0","X","X","X"],
#     ["0","X","0","X","X","X","0","X","X","X"],
#     ["0","X","0","X","X","X","0","X","X","X"],
#     ["0","X","0","X","X","X","0","X","X","X"],
#     ["0","X","0","X","X","X","0","X","X","X"],
#     ["0","0","0","X","X","X","0","0","0","S"],
# ]

# # EASY 4
# grid = [
#     ["X","0","0","0","0","0","0","0","X","X"],
#     ["X","0","X","X","X","X","X","0","X","X"],
#     ["X","0","X","X","X","X","X","0","X","X"],
#     ["X","0","X","X","X","X","X","0","X","X"],
#     ["X","0","X","X","X","X","X","0","X","X"],
#     ["X","0","X","X","X","X","0","0","X","X"],
#     ["X","X","0","0","0","0","0","X","X","X"],
#     ["X","X","0","0","0","0","0","0","X","X"],
#     ["0","0","0","0","0","0","0","0","X","X"],
#     ["0","0","0","0","0","0","0","0","0","S"],
# ]

# # EASY 5
# grid = [
#     ["X","X","X","X","X","X","X","0","0","X"],
#     ["X","X","X","X","X","X","X","0","0","X"],
#     ["0","0","0","0","0","0","0","0","0","X"],
#     ["0","X","X","X","X","X","0","0","0","X"],
#     ["0","X","X","X","X","X","0","0","0","X"],
#     ["0","X","0","0","0","X","0","0","0","X"],
#     ["0","X","0","X","0","X","0","0","0","X"],
#     ["0","X","0","X","0","X","0","0","0","X"],
#     ["0","X","X","X","0","X","X","X","0","X"],
#     ["0","0","0","0","0","X","X","X","0","S"],
# ]

# MEDIUM 1
grid = [
    ["0","0","0","0","0","0","0","0","0","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","0","0","X","X","X","X","X","X","0"],
    ["X","X","X","X","X","X","X","X","X","0"],
    ["X","X","X","X","X","X","X","X","X","0"],
    ["X","X","X","X","X","X","X","X","X","0"],
    ["X","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["0","X","X","X","X","X","X","X","X","0"],
    ["S","0","0","0","0","0","0","0","0","0"]
]

# # MEDIUM 2
# grid = [
#     ["X","X","X","X","X","X","X","X","X","X"],
#     ["0","X","X","X","X","X","X","0","0","0"],
#     ["0","X","X","X","X","X","X","0","X","0"],
#     ["0","X","X","X","X","X","X","0","X","0"],
#     ["0","0","0","0","0","0","0","0","0","0"],
#     ["0","X","X","X","X","X","X","0","X","X"],
#     ["0","X","X","X","X","X","X","0","X","X"],
#     ["0","X","X","X","X","X","X","0","X","X"],
#     ["0","X","X","X","X","X","X","0","0","0"],
#     ["0","X","X","X","X","X","X","X","X","S"]
# ]

# # MEDIUM 3
# grid = [
#     ["0","0","0","0","X","0","X","X","0","X"],
#     ["0","X","X","X","X","0","X","X","0","0"],
#     ["0","X","X","X","X","0","0","0","0","0"],
#     ["0","X","X","X","0","0","X","0","0","0"],
#     ["0","X","X","X","0","0","X","0","0","0"],
#     ["0","0","0","X","0","0","X","0","0","0"],
#     ["0","X","0","X","0","X","X","0","0","0"],
#     ["0","X","0","X","0","X","X","0","0","0"],
#     ["0","X","0","0","0","X","X","0","0","0"],
#     ["0","X","X","X","X","X","X","0","X","S"],
# ]

# # MEDIUM 4
# grid = [
#     ["X","X","X","0","0","0","0","X","X","0"],
#     ["0","0","X","0","X","X","0","X","X","0"],
#     ["0","0","X","0","X","X","0","X","X","0"],
#     ["0","0","X","0","X","X","0","0","X","0"],
#     ["0","0","X","0","0","X","0","0","X","0"],
#     ["0","0","X","X","X","X","0","0","X","0"],
#     ["0","0","X","X","X","X","X","0","X","0"],
#     ["0","0","0","0","0","0","0","0","X","0"],
#     ["0","X","X","X","X","X","X","X","X","0"],
#     ["0","0","0","0","0","0","0","0","0","S"],
# ]

# DIFFICULT 1
grid = [
    ["X","X","X","X","X","X","X","X","X","X"],
    ["X","X","0","0","0","0","0","0","0","X"],
    ["X","0","0","0","0","0","0","0","0","X"],
    ["X","0","X","X","X","X","X","X","0","X"],
    ["X","0","0","0","X","X","X","X","0","X"],
    ["X","0","X","0","X","X","X","X","0","X"],
    ["X","0","X","0","0","0","0","0","0","X"],
    ["X","X","0","0","0","0","0","S","X","X"],
    ["X","X","X","X","X","X","X","X","X","X"],
    ["X","X","X","X","X","X","X","X","X","X"]
]

# # DIFFICULT 2
# grid = [
#     ["X","0","0","0","0","0","0","0","X","X"],
#     ["X","0","0","0","0","0","0","0","0","X"],
#     ["X","0","0","X","X","0","X","X","0","X"],
#     ["X","0","0","X","X","0","X","X","0","X"],
#     ["X","0","0","X","X","0","X","X","0","X"],
#     ["X","0","0","X","X","0","0","0","0","0"],
#     ["0","0","0","X","X","0","X","X","0","0"],
#     ["0","0","0","X","X","0","X","X","0","0"],
#     ["0","0","0","X","X","0","X","X","0","0"],
#     ["S","0","0","0","0","0","0","0","0","0"]
# ]

# # DIFFICULT 3
# grid = [
#     ["X","X","X","X","X","X","X","X","0","0"],
#     ["0","0","0","0","X","X","X","X","0","X"],
#     ["0","0","0","0","0","0","X","X","0","0"],
#     ["0","0","0","0","0","0","X","X","0","0"],
#     ["0","X","X","X","X","X","X","X","0","0"],
#     ["0","X","X","X","X","X","X","X","X","0"],
#     ["0","X","X","X","X","X","X","X","X","0"],
#     ["0","0","0","0","0","0","0","X","X","0"],
#     ["0","X","X","X","X","0","X","X","X","0"],
#     ["S","X","X","X","X","0","0","0","0","0"]
# ]

# grid = solve_maze(grid, "ucs")
# print("-----------------------")
grid = solve_maze(grid, "a_star")