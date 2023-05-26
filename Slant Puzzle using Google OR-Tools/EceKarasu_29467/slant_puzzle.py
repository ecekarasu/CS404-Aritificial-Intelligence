from ortools.sat.python import cp_model
import copy
import time
from instances import get_instance

def is_valid_corner(i, j, corners):
    if (i < 0 or i > len(corners)-1) or (j < 0 or j > len(corners[0])-1):
        return False
    return True

def is_valid_cell(i, j, corners):
    if (i < 0 or i > len(corners)-2) or (j < 0 or j > len(corners[0])-2):
        return False
    return True

def num_intersects(i, j, corners, cells, model):
    num = 0
    bools = []
    for a in range(4):
        bools.append(model.NewBoolVar(str(i) + "_" + str(j) + "_" + str(a)))
    if corners[i][j] != "-1":
        cells_coords = [(i-1, j-1), (i, j), (i-1, j), (i, j-1)] # the cells surrounding the current corner
        for idx, c in enumerate(cells_coords):
            if is_valid_cell(c[0], c[1], corners): 
                # 1 -> /, 2 -> \
                if idx < 2: # (if top left and "\") or (if bottom right and "\")
                    model.Add(cells[(c[0], c[1])] == 2).OnlyEnforceIf(bools[idx])
                    model.Add(cells[(c[0], c[1])] != 2).OnlyEnforceIf(bools[idx].Not())
                else: # (if top right and "/") or (if bottom left and "/")
                    model.Add(cells[(c[0], c[1])] == 1).OnlyEnforceIf(bools[idx])
                    model.Add(cells[(c[0], c[1])] != 1).OnlyEnforceIf(bools[idx].Not())
            else:
                model.Add(bools[idx] == False)
        model.Add(sum(bools) == int(corners[i][j]))


    return model, bools

def has_loop(i, j, start, prev, corners, cells, model, visited, bools):
    if (i, j) == start and visited != []: # shows that i returned back to start
        # print("loop detected")
        model.Add(sum(bools) != len(bools))
        return model
    if not (visited == [] and (i, j) == start): # to not to append start at the first step
        visited.append((i, j))
    neighbor_corners = [(i-1, j-1), (i-1, j+1), (i+1, j+1), (i+1, j-1)] # top left, top right, bottom right, bottom left
    for idx, c in enumerate(neighbor_corners):
        if (is_valid_corner(c[0], c[1], corners)) and (c not in visited) and (c != prev) and (corners[c[0]][c[1]] != "0" and corners[c[0]][c[1]] != "1"):
            # 1 -> /, 2 -> \
            copy_bools = copy.deepcopy(bools)
            copy_visited = copy.deepcopy(visited)
            if idx == 0: # if top left, c = (i-1, j-1)
                cell_coords = (c[0], c[1])
                copy_bools.append(model.NewBoolVar(str(c[0]) + "_" + str(c[1]) + "_" + str(idx))) 
                model.Add(cells[(c[0], c[1])] == 2).OnlyEnforceIf(copy_bools[-1])
                model.Add(cells[(c[0], c[1])] != 2).OnlyEnforceIf(copy_bools[-1].Not())
                model = has_loop(c[0], c[1], start, (i, j), corners, cells, model, copy_visited, copy_bools)
            elif idx == 1: # top right, c = (i-1, j+1)
                cell_coords = (c[0], c[1]-1)
                copy_bools.append(model.NewBoolVar(str(c[0]) + "_" + str(c[1]-1) + "_" + str(idx))) 
                model.Add(cells[(c[0], c[1]-1)] == 1).OnlyEnforceIf(copy_bools[-1])
                model.Add(cells[(c[0], c[1]-1)] != 1).OnlyEnforceIf(copy_bools[-1].Not())
                model = has_loop(c[0], c[1], start, (i, j), corners, cells, model, copy_visited, copy_bools)
            elif idx == 2: # if bottom right, c = (i+1, j+1)
                cell_coords = (c[0]-1, c[1]-1)
                copy_bools.append(model.NewBoolVar(str(c[0]-1) + "_" + str(c[1]-1) + "_" + str(idx))) 
                model.Add(cells[(c[0]-1, c[1]-1)] == 2).OnlyEnforceIf(copy_bools[-1])
                model.Add(cells[(c[0]-1, c[1]-1)] != 2).OnlyEnforceIf(copy_bools[-1].Not())
                model = has_loop(c[0], c[1], start, (i, j), corners, cells, model, copy_visited, copy_bools)
            elif idx == 3: # bottom left, c = (i+1, j-1)
                cell_coords = (c[0]-1, c[1])
                copy_bools.append(model.NewBoolVar(str(c[0]-1) + "_" + str(c[1]) + "_" + str(idx))) 
                model.Add(cells[(c[0]-1, c[1])] == 1).OnlyEnforceIf(copy_bools[-1])
                model.Add(cells[(c[0]-1, c[1])] != 1).OnlyEnforceIf(copy_bools[-1].Not())
                model = has_loop(c[0], c[1], start, (i, j), corners, cells, model, copy_visited, copy_bools)
                
    return model

def solve_puzzle(corners, num_rows_corners, num_cols_corners):
    corners = [[x if x != "*" else "-1" for x in row] for row in corners]
    bools = [[x for x in row] for row in corners]

    # Creates the model
    model = cp_model.CpModel()

    # Creates the variables
    cells = {}
    for i in range(num_rows_corners-1):
        for j in range(num_rows_corners-1):
            name = "cells[(" + str(i) + ", " + str(j) + ")]"
            cells[(i, j)] = model.NewIntVar(1, 2, name)

    # Add constraints to enforce the corners' rules
    for i in range(num_rows_corners):
        for j in range(num_cols_corners):
            # number of intersections constraint
            model, returned_bools = num_intersects(i, j, corners, cells, model)
            bools[i][j] = returned_bools

    for i in range(num_rows_corners):
        for j in range(num_cols_corners):
            # loop constraint
            model = has_loop(i, j, (i, j), (-1, -1), corners, cells, model, [], [])

    # Creates a solver
    solver = cp_model.CpSolver()
    # Solves the model
    status = solver.Solve(model)

    return solver, status, cells

def print_info(corners, instance_no, solver, status, cells, num_rows_corners, num_cols_corners, total_time):
    if instance_no > 9:
        level = "DIFFICULT"
    elif instance_no > 4:
        level = "NORMAL"
    else:
        level = "EASY"

    print(level, "INSTANCE NO", (instance_no%5)+1)
    print("Original puzzle is:")
    for row in corners:
        print(row)
    # stats = solver.ResponseStats()
    # stats = solver.ResponseProto()
    # print(stats)
    print("Solved puzzle is:")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for i in range(num_rows_corners-1):
            for j in range(num_cols_corners-1):
                if solver.Value(cells[(i, j)]) == 1:
                    print("/", end="")
                else: # solver.Value(cells[(i, j)]) == 2
                    print("\\", end="")
            print("")
    else:
        print("No solution found!")
    print("The CPU time is %s seconds" % total_time)
    print("----------")

instances = get_instance()
for instance_no in range(len(instances)):
    start_time = time.time()
    corners = instances[instance_no]
    num_rows_corners = len(corners)
    num_cols_corners = len(corners[0])
    solver, status, cells = solve_puzzle(corners, num_rows_corners, num_cols_corners)
    total_time = time.time() - start_time
    print_info(corners, instance_no, solver, status, cells, num_rows_corners, num_cols_corners, total_time)