import copy
import math # Import math for sqrt
import heapq # Import heapq for priority queue
import json # Import json for outputting commands
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class Node:
    def __init__(self, row, col, parent=None):
        self.indice = [row, col]
        self.parent = parent
        # Costs
        self.g = 0 # Cost from start to this node
        self.h = 0 # Heuristic cost from this node to goal
        self.f = 0 # Total cost (g + h)

    # Used for comparing nodes in the open list (priority queue)
    def __lt__(self, other):
        return self.f < other.f

    # Used for checking node equality in lists
    def __eq__(self, other):
        return self.indice == other.indice

    # Used for hashing nodes, necessary for using nodes in sets or dicts
    def __hash__(self):
        return hash(tuple(self.indice))

# Define movement directions for visualization
movement_directions = [
    ("cima", -1, 0), ("baixo", 1, 0), ("esquerda", 0, -1), ("direita", 0, 1),  # Cardinal
    ("diagonal superior esquerda", -1, -1), ("diagonal superior direita", -1, 1), ("diagonal inferior esquerda", 1, -1), ("diagonal inferior direita", 1, 1) # Diagonal
]


mapa = [
    ['C','','','','B',''],
    ['','B','','','',''],
    ['','','F','','',''],
    ['','','','B','B',''],
    ['','','','A','',''],
    ['','','','','','S']
]

def is_valid(row, col, grid):
    """Checks if a cell is within grid bounds."""
    return 0 <= row < len(grid) and 0 <= col < len(grid[0])

def is_obstacle(row, col, grid):
    """Checks if a cell is an obstacle."""
    # 'B' is an obstacle
    return grid[row][col] == 'B'

def get_neighbors(node, grid):
    """Returns valid neighbors of a node (up, down, left, right, diagonals)."""
    neighbors = []
    # Possible movements: (row_change, col_change)
    movements = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal
        (-1, -1), (-1, 1), (1, -1), (1, 1) # Diagonal
    ]

    for dr, dc in movements:
        new_row, new_col = node.indice[0] + dr, node.indice[1] + dc

        # For A* logic, we only add valid, non-obstacle neighbors
        if is_valid(new_row, new_col, grid) and not is_obstacle(new_row, new_col, grid):
            neighbors.append(Node(new_row, new_col, parent=node))

    return neighbors

def calculate_h(node, goal):
    """Calculates heuristic (Euclidean distance) from node to goal."""
    row1, col1 = node.indice
    row2, col2 = goal.indice
    # Euclidean distance
    return math.sqrt((row2 - row1)**2 + (col2 - col1)**2)

def get_step_cost(current_node, neighbor_node, grid):
    """Calculates the cost to move from current_node to neighbor_node."""
    dr = abs(current_node.indice[0] - neighbor_node.indice[0])
    dc = abs(current_node.indice[1] - neighbor_node.indice[1])

    # Base cost: 1 for cardinal, sqrt(2) approx 1.414 for diagonal
    base_cost = 1.414 if dr > 0 and dc > 0 else 1

    # Add cost for 'A' (semi-barrier)
    if grid[neighbor_node.indice[0]][neighbor_node.indice[1]] == 'A':
        base_cost += 1 # Example: add 1 to cost

    # 'F' (fruit) doesn't add extra cost in this basic implementation,
    # but could be handled in a more advanced state representation.
    # if grid[neighbor_node.indice[0]][neighbor_node.indice[1]] == 'F':
    #    pass # No extra cost for fruit

    return base_cost

def astar(grid):
    """Implements the A* pathfinding algorithm (returns final path)."""
    start_row, start_col = -1, -1
    goal_row, goal_col = -1, -1

    # Find start and goal positions
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'C':
                start_row, start_col = r, c
            elif grid[r][c] == 'S':
                goal_row, goal_col = r, c

    if start_row == -1 or goal_row == -1:
        print("Start ('C') or Goal ('S') not found on the map.")
        return None

    start_node = Node(start_row, start_col)
    goal_node = Node(goal_row, goal_col)

    open_list = []
    heapq.heappush(open_list, start_node)

    closed_list = set()

    open_list_dict = {start_node: start_node}

    while open_list:
        current_node = heapq.heappop(open_list)
        del open_list_dict[current_node]

        closed_list.add(current_node)

        if current_node == goal_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.indice)
                current = current.parent
            path.reverse() # Reverse path to get from start to goal
            return path

        neighbors = get_neighbors(current_node, grid)

        for neighbor in neighbors:
            if neighbor in closed_list:
                continue

            tentative_g = current_node.g + get_step_cost(current_node, neighbor, grid)

            if neighbor in open_list_dict and tentative_g >= open_list_dict[neighbor].g:
                continue

            neighbor.parent = current_node
            neighbor.g = tentative_g
            neighbor.h = calculate_h(neighbor, goal_node)
            neighbor.f = neighbor.g + neighbor.h

            if neighbor not in open_list_dict:
                heapq.heappush(open_list, neighbor)
                open_list_dict[neighbor] = neighbor
            else:
                 pass # Update handled by the continue checks

    # Path not found
    return None

def astar_visualize(grid):
    """Implements A* pathfinding and records attempted moves for visualization."""
    start_row, start_col = -1, -1
    goal_row, goal_col = -1, -1

    # Find start and goal positions
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'C':
                start_row, start_col = r, c
            elif grid[r][c] == 'S':
                goal_row, goal_col = r, c

    if start_row == -1 or goal_row == -1:
        print("Start ('C') or Goal ('S') not found on the map.")
        return [], [] # Return empty path and visualization steps

    start_node = Node(start_row, start_col)
    goal_node = Node(goal_row, goal_col)

    open_list = []
    heapq.heappush(open_list, start_node)

    closed_list = set()

    open_list_dict = {start_node: start_node}

    # List to store steps for visualization
    visualization_steps = []

    while open_list:
        current_node = heapq.heappop(open_list)
        del open_list_dict[current_node]

        closed_list.add(current_node)

        # Add step: Move to current node (part of the explored path)
        visualization_steps.append({'type': 'move', 'coords': current_node.indice})

        if current_node == goal_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.indice)
                current = current.parent
            path.reverse() # Reverse path to get from start to goal
            return path, visualization_steps

        # Expand neighbors and record attempts
        for move_name, dr, dc in movement_directions:
            new_row, new_col = current_node.indice[0] + dr, current_node.indice[1] + dc

            # Record attempted move
            visualization_steps.append({'type': 'attempt', 'from': current_node.indice, 'to': [new_row, new_col], 'direction': move_name})

            # Check if the attempted move is valid and not an obstacle
            if not is_valid(new_row, new_col, grid) or is_obstacle(new_row, new_col, grid):
                # This attempted move is invalid/obstacle, record as blocked
                visualization_steps.append({'type': 'blocked', 'coords': [new_row, new_col]})
                continue # Skip this neighbor for A* logic

            neighbor = Node(new_row, new_col, parent=current_node)

            if neighbor in closed_list:
                # This attempted move leads to a node already processed, record as skipped
                visualization_steps.append({'type': 'skipped_closed', 'coords': [new_row, new_col]})
                continue

            tentative_g = current_node.g + get_step_cost(current_node, neighbor, grid)

            if neighbor in open_list_dict and tentative_g >= open_list_dict[neighbor].g:
                # This attempted move leads to a node in open list but the new path is NOT better, record as skipped
                visualization_steps.append({'type': 'skipped_open', 'coords': [new_row, new_col]})
                continue

            # If the move is valid and leads to a better path or a new node:
            # Update neighbor's parent, g-cost, and f-cost for A* logic
            neighbor.parent = current_node
            neighbor.g = tentative_g
            neighbor.h = calculate_h(neighbor, goal_node)
            neighbor.f = neighbor.g + neighbor.h

            if neighbor not in open_list_dict:
                # Add new node to open list, record as added
                heapq.heappush(open_list, neighbor)
                open_list_dict[neighbor] = neighbor
                visualization_steps.append({'type': 'add_open', 'coords': [new_row, new_col]})
            else:
                 pass # A* logic handles the update implicitly through the continue checks


    # Path not found
    return None, visualization_steps # Return empty path if none found

def translate_path_to_commands(path):
    """Translates a sequence of grid coordinates into movement commands."""
    commands = []
    for i in range(len(path) - 1):
        current_pos = path[i]
        next_pos = path[i+1]

        dr = next_pos[0] - current_pos[0]
        dc = next_pos[1] - current_pos[1]

        if dr == -1 and dc == 0:
            commands.append("cima")
        elif dr == 1 and dc == 0:
            commands.append("baixo")
        elif dr == 0 and dc == -1:
            commands.append("esquerda")
        elif dr == 0 and dc == 1:
            commands.append("direita")
        elif dr == -1 and dc == -1:
            commands.append("diagonal superior esquerda")
        elif dr == -1 and dc == 1:
            commands.append("diagonal superior direita")
        elif dr == 1 and dc == -1:
            commands.append("diagonal inferior esquerda")
        elif dr == 1 and dc == 1:
            commands.append("diagonal inferior direita")
    return commands

class AStarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle request for final path (existing functionality)
        if self.path == '/get_path':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Use the original astar function for the final path
            found_path = astar(mapa)

            if found_path:
                movement_commands = translate_path_to_commands(found_path)
                response_data = json.dumps(movement_commands)
            else:
                response_data = json.dumps([]) # Return empty list if no path found

            self.wfile.write(response_data.encode('utf-8'))

        # Handle request for visualization steps
        elif self.path == '/get_visualization_steps':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Use the new visualization function
            _, visualization_steps = astar_visualize(mapa)
            response_data = json.dumps(visualization_steps)

            self.wfile.write(response_data.encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run(server_class=HTTPServer, handler_class=AStarHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping httpd server.')

if __name__ == '__main__':
    run()

      