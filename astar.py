import pygame
from queue import PriorityQueue
import math
import tkinter as tk
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SILVER = (60,60,60)

# Value Codes 
START = -1
END = -2

OPEN = 0
BLOCKED = 1
PATH = 3
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 5

# to make the indexing look better
ROW = 0
COL = 1

DIAGONAL_COST = math.sqrt(2)
ORTHOGONAL_COST = 1

# Initialize pygame
pygame.init()

GRID_SIZE = 40
# Set title of screen
pygame.display.set_caption("A Star")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

grid = []
for row in range(GRID_SIZE):
    grid.append([])
    for column in range(GRID_SIZE):
        grid[row].append(0)

class Cell:
    def __init__(self):
        self.g = float("inf")
        self.f = float("inf")
        self.parent_i = -1
        self.parent_j = -1
        self.on_closed_list = False
        self.valid_neighbors = []

cell_info = []
for row in range(GRID_SIZE):
    cell_info.append([])
    for column in range(GRID_SIZE):
        cell_info[row].append(Cell())

# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [int(WIDTH * GRID_SIZE * 1.26), int(HEIGHT * GRID_SIZE * 1.26)]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
start_coords = (-1,-1)
end_coords = (-1, -1)

def is_valid(i, j):
    if not(i >= 0 and i < GRID_SIZE and j >= 0 and j < GRID_SIZE):
        return False
    if grid[i][j] == BLOCKED:
        return False
    return True

def euclidean_heuristic(point, dest, weight):
  return math.sqrt(((point[ROW] - dest[ROW]) * (point[ROW] - dest[ROW])) + ((point[COL] - dest[COL]) * (point[COL] - dest[COL]))) * weight

def manhattan_heuristic(point, dest, weight):
  return abs(point[ROW] - dest[ROW]) + abs(point[COL] - dest[COL]) * weight

def chebbyshev_heuristic(point, dest, weight):
  return max(abs(point[ROW] - dest[ROW]), abs(point[COL] - dest[COL])) * weight

def octile_heuristic(point, dest, weight):
    xDiff = abs(point[ROW] - dest[ROW])
    yDiff = abs(point[COL] - dest[COL])
    return ((min(xDiff, yDiff) * math.sqrt(weight * weight * 2)) + max(xDiff, yDiff) - min(xDiff, yDiff)) * weight

HEURISTIC = euclidean_heuristic

heuristic_table = {"euclidean": euclidean_heuristic, "manhattan": manhattan_heuristic, 
                    "chebbyshev": chebbyshev_heuristic, "octile": octile_heuristic }

def process_valid_neighbors():
    for i in range(0, GRID_SIZE):
        for j in range(0, GRID_SIZE):

            # reset from previous run
            cell_info[i][j].valid_neighbors.clear()
            cell_info[i][j].g = float("inf")
            cell_info[i][j].f = float("inf")
            cell_info[i][j].on_closed_list = False
            cell_info[i][j].parent_i = -1
            cell_info[i][j].parent_j = -1

            if grid[i][j] == PATH: # clean up last path
                grid[i][j] = OPEN

            # N case
            if (is_valid(i, j + 1)):
              cell_info[i][j].valid_neighbors.append((i, j + 1))
            # W case
            if (is_valid(i - 1, j)):
              cell_info[i][j].valid_neighbors.append((i - 1, j))
            # E case
            if (is_valid(i + 1, j)):
              cell_info[i][j].valid_neighbors.append((i + 1, j))
            # S case
            if (is_valid(i, j - 1)):
              cell_info[i][j].valid_neighbors.append((i, j - 1))
            # N.W case
            if (is_valid(i - 1, j + 1) and is_valid(i, j + 1) and is_valid(i - 1, j)):
              cell_info[i][j].valid_neighbors.append((i - 1, j + 1))
            # N.E case
            if (is_valid(i + 1, j + 1) and is_valid(i, j + 1) and is_valid(i + 1, j)):
              cell_info[i][j].valid_neighbors.append((i + 1, j + 1))
            # S.W case
            if (is_valid(i - 1, j - 1) and is_valid(i - 1, j) and is_valid(i, j - 1)):
              cell_info[i][j].valid_neighbors.append((i - 1, j - 1))
            # S.E case
            if (is_valid(i + 1, j - 1) and is_valid(i + 1, j) and is_valid(i, j - 1)):
              cell_info[i][j].valid_neighbors.append((i + 1, j - 1))
              

def build_path(shortest_path, end):
    current_i = cell_info[end[ROW]][end[COL]].parent_i
    current_j = cell_info[end[ROW]][end[COL]].parent_j
    while (current_i != start_coords[ROW] or current_j != start_coords[COL]):
        shortest_path.append((current_i, current_j))
        temp_i = cell_info[current_i][current_j].parent_i
        temp_j = cell_info[current_i][current_j].parent_j
        current_i = temp_i
        current_j = temp_j
    return shortest_path

def solve_astar():
    open_list = PriorityQueue()
    open_list.put((0.0, start_coords))
    curr_i, curr_j = start_coords
    cell_info[curr_i][curr_j].parent_i = curr_i
    cell_info[curr_i][curr_j].parent_j = curr_j
    cell_info[curr_i][curr_j].f = 0.0
    cell_info[curr_i][curr_j].g = 0.0

    shortest_path = []

    while not open_list.empty():
        current = open_list.get()
        curr_i = current[1][ROW]
        curr_j = current[1][COL]
        cell_info[curr_i][curr_j].on_closed_list = True
        if current[1] == end_coords:
            return build_path(shortest_path, end_coords)
        current_cell = cell_info[curr_i][curr_j]
        neighbor_count = len(current_cell.valid_neighbors)
        for neighbor_index in range(0, neighbor_count):
            next_node = current_cell.valid_neighbors[neighbor_index]
            newG = 0.0
            newH = 0.0
            newF = 0.0
            if not cell_info[next_node[ROW]][next_node[COL]].on_closed_list:
                if next_node[ROW] != curr_i and next_node[COL] != curr_j:
                    newG = cell_info[curr_i][curr_j].g + DIAGONAL_COST
                else:
                    newG = cell_info[curr_i][curr_j].g + ORTHOGONAL_COST
                newH = heuristic_table[selected_heuristic.get()](next_node, end_coords, weight_variable.get())
                newF = newH + newG
                if cell_info[next_node[ROW]][next_node[COL]].f > newF:
                    cell_info[next_node[ROW]][next_node[COL]].parent_i = curr_i
                    cell_info[next_node[ROW]][next_node[COL]].parent_j = curr_j
                    cell_info[next_node[ROW]][next_node[COL]].f = newF
                    cell_info[next_node[ROW]][next_node[COL]].g = newG
                    open_list.put((newF, next_node))
    return []

def verify_coordinates(row, col):
    if row < 0 or row >= GRID_SIZE:
        return False
    if col < 0 or col >= GRID_SIZE:
        return False
    return True

# -------- tkinker -----------
window = tk.Tk()
window.geometry("220x150")
window.title("Options")
selected_heuristic = tk.StringVar(window)
heuristic_options = [
    "euclidean",
    "manhattan",
    "chebbyshev",
    "octile"
]
sel_heur_text = tk.StringVar()
sel_heur_label = tk.Label( window, textvariable=sel_heur_text)
sel_heur_text.set("Heuristic Method:")
sel_heur_label.pack()
selected_heuristic.set(heuristic_options[0]) # euclidean default

heuristic_dropdown = tk.OptionMenu(window, selected_heuristic, *heuristic_options)
heuristic_dropdown.pack()

sel_heur_text = tk.StringVar()
sel_heur_label = tk.Label( window, textvariable=sel_heur_text)
sel_heur_text.set("Heuristic Value:")
sel_heur_label.pack()

weight_variable = tk.DoubleVar()
weight_variable.set(1.0)
heuristic_weight = tk.Scale(window, from_=-10.0, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, variable=weight_variable)
heuristic_weight.pack()

smoothing_flag = tk.IntVar()
smoothing_cb = tk.Checkbutton(window, text='Smoothing',variable=smoothing_flag, onvalue=1, offvalue=0)
smoothing_cb.pack()

window.mainloop()

# -------- main loop -----------
while not done:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:  
            done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if (start_coords[ROW] != -1 or start_coords[COL] != -1) and \
                    (end_coords[ROW] != -1 or end_coords[COL] != -1):
                process_valid_neighbors()
                path = solve_astar()
                if len(path) == 0:
                    print("a star failed")
                else:
                    for square in path:
                        grid[square[ROW]][square[COL]] = PATH
            else:
                print("ERROR: NO START AND/OR END POINT")

    if pygame.mouse.get_pressed()[0]: # left mouse button
        pos = pygame.mouse.get_pos()
        # Change the x/y screen coordinates to grid coordinates
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        if verify_coordinates(row, column) == True:
            # Set that location to BLOCKED
            grid[row][column] = BLOCKED
            if row == start_coords[ROW] and column == start_coords[COL]:
                start_coords = (-1, -1)

            if row == end_coords[ROW] and column == end_coords[COL]:
                end_coords = (-1, -1)
    
    if pygame.mouse.get_pressed()[2]: # right mouse button
        pos = pygame.mouse.get_pos()
        # Change the x/y screen coordinates to grid coordinates
        column = pos[ROW] // (WIDTH + MARGIN)
        row = pos[COL] // (HEIGHT + MARGIN)
        if verify_coordinates(row, column) == True:
            # Set that location to one
            grid[row][column] = OPEN
            if row == start_coords[ROW] and column == start_coords[COL]:
                start_coords = (-1, -1)

            if row == end_coords[ROW] and column == end_coords[COL]:
                end_coords = (-1, -1)

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_s]:
        pos = pygame.mouse.get_pos()
        column = pos[ROW] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        if verify_coordinates(row, column) == True:
            if (start_coords[ROW] != -1 and start_coords[COL] != -1):
                grid[start_coords[ROW]][start_coords[COL]] = OPEN
            if (grid[row][column] == END):
                end_coords = (-1,-1)
            start_coords = (row, column)
            grid[row][column] = START

    if pressed[pygame.K_e]:
        pos = pygame.mouse.get_pos()
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)
        if verify_coordinates(row, column) == True:
            if (end_coords[ROW] != -1 and end_coords[COL] != -1):
                grid[end_coords[ROW]][end_coords[COL]] = OPEN
            if (grid[row][column] == START):
                start_coords = (-1,-1)
            end_coords = (row, column)
            grid[row][column] = END

    screen.fill(BLACK)

    # draw grid
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            color = WHITE
            if grid[row][column] == BLOCKED:
                color = SILVER
            elif grid[row][column] == START:
                color = GREEN
            elif grid[row][column] == END:
                color = RED
            elif grid[row][column] == PATH:
                color = BLUE
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH, HEIGHT])
    clock.tick(60)
    pygame.display.flip()
 
pygame.quit()