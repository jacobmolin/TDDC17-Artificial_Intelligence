import sys
import random as Randy
from lab1.liuvacuum import *

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3

def direction_to_string(cdr):
    cdr %= 4
    return  "NORTH" if cdr == AGENT_DIRECTION_NORTH else\
            "EAST"  if cdr == AGENT_DIRECTION_EAST else\
            "SOUTH" if cdr == AGENT_DIRECTION_SOUTH else\
            "WEST" #if dir == AGENT_DIRECTION_WEST

"""
Internal state of a vacuum agent
"""
class MyAgentState:

    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [[AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1

        # Metadata
        self.world_width = width
        self.world_height = height


    """
    Update perceived agent location
    """
    def update_position(self, bump):
        if not bump and self.last_action == ACTION_FORWARD:
            if self.direction == AGENT_DIRECTION_EAST:
                self.pos_x += 1
            elif self.direction == AGENT_DIRECTION_SOUTH:
                self.pos_y += 1
            elif self.direction == AGENT_DIRECTION_WEST:
                self.pos_x -= 1
            elif self.direction == AGENT_DIRECTION_NORTH:
                self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """
    def update_world(self, x, y, info):
        self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """
    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print() # Newline
        print() # Delimiter post-print

"""
Vacuum agent
"""
class MyVacuumAgent2(Agent):

    def __init__(self, world_width, world_height, log):
        super().__init__(self.execute)
        self.initial_random_actions = 10
        self.iteration_counter = world_height * world_width * 2
        self.state = MyAgentState(world_width, world_height)
        self.log = log
        self.tiles_visited = 0
        self.tile_amount = sys.maxsize
        self.width = sys.maxsize / 2
        self.height = sys.maxsize / 2
        self.route = []
        self.largest_world_dimension = 1000

    def move_to_random_start_position(self, bump):
        action = random()

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:   # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT
        elif action < 0.3333333: # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
        else:                    # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD

    # 
    def get_info(self, current_coords, current_direction):
        offset_l_r_f_b = [
            [(-1, 0), (1, 0), (0, -1), (0, 1)],
            [(0, -1), (0, 1), (1, 0), (-1, 0)],
            [(1, 0), (-1, 0), (0, 1), (0, -1)],
            [(0, 1), (0, -1), (-1, 0), (1, 0)]
        ][current_direction]

        info_to_left = self.state.world[current_coords[0] + (offset_l_r_f_b[0])[0]][current_coords[1] + (offset_l_r_f_b[0])[1]]
        info_to_right = self.state.world[current_coords[0] + (offset_l_r_f_b[1])[0]][current_coords[1] + (offset_l_r_f_b[1])[1]]
        info_to_forward = self.state.world[current_coords[0] + (offset_l_r_f_b[2])[0]][current_coords[1] + (offset_l_r_f_b[2])[1]]
        info_to_backward = self.state.world[current_coords[0] + (offset_l_r_f_b[3])[0]][current_coords[1] + (offset_l_r_f_b[3])[1]]
                    
        return offset_l_r_f_b, info_to_left, info_to_right, info_to_forward, info_to_backward

    # Calculate a route between two points
    def calc_route(self, start, end):
        current_coords = start
        current_direction = self.state.direction
        # amount_steps_x = abs(end[0] - start[0])
        # amount_steps_y = abs(end[1] - start[1])

        self.log("going from {} to {}".format(start, end))

        counter = 0

        while (
            len(self.route) < 15 and
            (abs(current_coords[0] - end[0]) > 0 or
            abs(current_coords[1] - end[1]) > 0)
        ):
            if (
                current_coords[0] < 1 or current_coords[0] > self.width or
                current_coords[1] < 1 or current_coords[1] > self.height
            ):
                break

            offset_l_r_f_b, info_to_left, info_to_right, info_to_forward, info_to_backward = self.get_info(current_coords, current_direction)

            # Want to move directly NORTH or SOUTH
            if end[0] == current_coords[0]:
                # Want to go NORTH
                if end[1] < current_coords[1]:
                    if current_direction == AGENT_DIRECTION_NORTH and info_to_forward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[2])[1])
                        current_direction = AGENT_DIRECTION_NORTH
                        continue
                    elif current_direction == AGENT_DIRECTION_EAST and info_to_left != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[0])[1])
                        current_direction = AGENT_DIRECTION_NORTH
                        continue
                    elif current_direction == AGENT_DIRECTION_SOUTH and info_to_backward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[3])[1])
                        current_direction = AGENT_DIRECTION_NORTH
                        continue
                    elif current_direction == AGENT_DIRECTION_WEST and info_to_right != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[1])[1])
                        current_direction = AGENT_DIRECTION_NORTH
                        continue

                # Want to go SOUTH
                else:
                    if current_direction == AGENT_DIRECTION_NORTH and info_to_backward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[3])[1])
                        current_direction = AGENT_DIRECTION_SOUTH
                        continue
                    elif current_direction == AGENT_DIRECTION_EAST and info_to_right != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[1])[1])
                        current_direction = AGENT_DIRECTION_SOUTH
                        continue
                    elif current_direction == AGENT_DIRECTION_SOUTH and info_to_forward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[2])[1])
                        current_direction = AGENT_DIRECTION_SOUTH
                        continue
                    elif current_direction == AGENT_DIRECTION_WEST and info_to_left != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[0])[1])
                        current_direction = AGENT_DIRECTION_SOUTH
                        continue

            # Want to go WEST, NORTH or SOUTH. If not possible, move EAST              
            elif end[0] < current_coords[0]:
                if current_direction == AGENT_DIRECTION_NORTH:
                    if info_to_left != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[0])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_WEST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_forward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[2])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_backward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[3])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_right != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[1])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_EAST
                            continue

                elif current_direction == AGENT_DIRECTION_EAST:
                    if info_to_backward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[3])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_WEST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_left != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[0])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_right != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[1])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_forward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[2])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_EAST
                            continue

                elif current_direction == AGENT_DIRECTION_SOUTH:
                    if info_to_right != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[1])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_WEST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_backward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[3])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_forward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[2])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_left != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[0])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_EAST
                            continue

                else:
                    if info_to_forward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[2])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_WEST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_right != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[1])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_left != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[0])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_backward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[3])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_EAST
                            continue

            # Want to move EAST, NORTH or SOUTH. If not possible, move WEST
            else:
                if current_direction == AGENT_DIRECTION_NORTH:
                    if info_to_right != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[1])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_EAST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_forward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[2])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_backward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[3])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_left != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[0])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_WEST
                            continue

                elif current_direction == AGENT_DIRECTION_EAST:
                    if info_to_forward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[2])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_EAST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_left != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[0])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_right != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[1])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_backward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[3])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_WEST
                            continue
                        

                elif current_direction == AGENT_DIRECTION_SOUTH:
                    if info_to_left != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[0])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_EAST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_backward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[3])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_forward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[2])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_right != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[1])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_WEST
                            continue

                else:
                    if info_to_backward != AGENT_STATE_WALL:
                        self.route.extend([ACTION_TURN_RIGHT, ACTION_TURN_RIGHT, ACTION_FORWARD])
                        current_coords = (current_coords[0] + (offset_l_r_f_b[3])[0], current_coords[1])
                        current_direction = AGENT_DIRECTION_EAST
                        continue
                    else:
                        if end[1] <= current_coords[1] and info_to_right != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_RIGHT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[1])[1])
                            current_direction = AGENT_DIRECTION_NORTH
                            continue
                        elif end[1] > current_coords[1] and info_to_left != AGENT_STATE_WALL:
                            self.route.extend([ACTION_TURN_LEFT, ACTION_FORWARD])
                            current_coords = (current_coords[0], current_coords[1] + (offset_l_r_f_b[0])[1])
                            current_direction = AGENT_DIRECTION_SOUTH
                            continue
                        elif info_to_forward != AGENT_STATE_WALL:
                            self.route.extend([ACTION_FORWARD])
                            current_coords = (current_coords[0] + (offset_l_r_f_b[2])[0], current_coords[1])
                            current_direction = AGENT_DIRECTION_WEST
                            continue

            # If the agent cannot find the next step, randomize
            for i in range(3):
                rand_index = Randy.randint(0, 3)
                rand_dir = [
                    [ACTION_TURN_LEFT, ACTION_FORWARD],
                    [ACTION_TURN_RIGHT, ACTION_FORWARD],
                    [ACTION_FORWARD],
                    [ACTION_TURN_LEFT, ACTION_TURN_LEFT, ACTION_FORWARD]
                ][rand_index]
                self.route.extend(rand_dir)
            break

    def execute(self, percept):

        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log("Moving to random start position ({} steps left)".format(self.initial_random_actions))
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK

        ########################
        # START MODIFYING HERE #
        ########################
        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
            return ACTION_NOP

        self.log("\nPosition: ({}, {})\t\tDirection: {}".format(self.state.pos_x, self.state.pos_y,
                                                              direction_to_string(self.state.direction)))

        self.iteration_counter -= 1

        # Track position of agent
        self.state.update_position(bump)

        # Increase unique tiles visited (except obstacles)
        if self.state.world[self.state.pos_x][self.state.pos_y] == AGENT_STATE_UNKNOWN:
            self.tiles_visited += 1    
        self.log('tiles visited: {}'.format(self.tiles_visited))

        # Updating world
        if bump:
            # Get an xy-offset pair based on where the agent is facing
            #          NORTH    EAST   SOUTH     WEST
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]
            offset_x = self.state.pos_x + offset[0]
            offset_y = self.state.pos_y + offset[1]

            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(offset_x, offset_y, AGENT_STATE_WALL)

            # Update percieved world dimensions if you go outside known world
            if self.state.direction == AGENT_DIRECTION_EAST and self.state.world[offset_x][self.state.pos_y] != AGENT_STATE_UNKNOWN:
                if self.width > self.largest_world_dimension:
                    self.width = self.state.pos_x
                else:
                    self.width = max(self.width, self.state.pos_x)
            elif self.state.direction == AGENT_DIRECTION_SOUTH and self.state.world[self.state.pos_x][offset_y] != AGENT_STATE_UNKNOWN:
                if self.height > self.largest_world_dimension:
                    self.height = self.state.pos_y
                else:
                    self.height = max(self.height, self.state.pos_y)
            
            # Update tile amount of percieved world
            self.tile_amount = self.width * self.height
            
            # Increase tiles visited for an obstacle
            if (
                (self.width < self.largest_world_dimension and offset_x >= 1 and offset_x <= self.width) and
                (self.height < self.largest_world_dimension and offset_y >= 1 and offset_y <= self.height)
            ):
                # self.log("Visited obstacle on: {}".format((offset_x, offset_y)))
                self.tiles_visited += 1

            # Stop following route if bump
            if len(self.route) > 0:
                self.route = []
            
        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        elif home:  
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_HOME)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)

        # Debug
        self.state.print_world_debug()

        #Check where can go
        # Get an xy-offset pair to the left, right, forward and backward based on where the agent is facing
        offset_l_r_f_b = [
            [(-1, 0), (1, 0), (0, -1), (0, 1)],
            [(0, -1), (0, 1), (1, 0), (-1, 0)],
            [(1, 0), (-1, 0), (0, 1), (0, -1)],
            [(0, 1), (0, -1), (-1, 0), (1, 0)]
        ][self.state.direction]
        
        # Information about whats to the left, right and forward
        info_to_left = self.state.world[self.state.pos_x + (offset_l_r_f_b[0])[0]][self.state.pos_y + (offset_l_r_f_b[0])[1]]
        info_to_right = self.state.world[self.state.pos_x + (offset_l_r_f_b[1])[0]][self.state.pos_y + (offset_l_r_f_b[1])[1]]
        info_to_forward = self.state.world[self.state.pos_x + (offset_l_r_f_b[2])[0]][self.state.pos_y + (offset_l_r_f_b[2])[1]]

        # Get direction pair to the left and right of agent
        new_direction_left_right = [
            (AGENT_DIRECTION_WEST, AGENT_DIRECTION_EAST),
            (AGENT_DIRECTION_NORTH, AGENT_DIRECTION_SOUTH),
            (AGENT_DIRECTION_EAST, AGENT_DIRECTION_WEST),
            (AGENT_DIRECTION_SOUTH, AGENT_DIRECTION_NORTH)
        ][self.state.direction]


        self.log("tiles left: {}".format((self.tile_amount - self.tiles_visited - 1)))
        self.log("width: {}".format(self.width))
        self.log("height: {}".format(self.height))

        # Decide action
        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK

        # If a route exists, follow it
        if len(self.route) > 0 and not bump and not home:
            self.log("route: {}".format(self.route))
            action = self.route.pop(0)
            
            if action == ACTION_TURN_LEFT:
                self.state.direction = new_direction_left_right[0]
            elif action == ACTION_TURN_RIGHT:
                self.state.direction = new_direction_left_right[1]

            self.state.last_action = action
            return action

        # If all tiles are found, calculate route home
        if (self.tile_amount - self.tiles_visited - 1) <= 0:
            if home:
                #Stop at home
                self.iteration_counter = 0
                self.log("Parked at home!")
                self.state.last_action = ACTION_NOP
                return ACTION_NOP
            elif len(self.route) == 0:
                #calculate way home
                home_coords = (1, 1)
                for y in range(self.height):
                    for x in range(self.width):
                        if self.state.world[x][y] == AGENT_STATE_HOME:
                            home_coords = (x, y)
                            break

                self.calc_route((self.state.pos_x, self.state.pos_y), home_coords)

        if info_to_forward == AGENT_STATE_UNKNOWN:
            # Stop following route if unknown tiles are found
            if len(self.route) > 0: 
                self.route = []                
            
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD
        
        elif info_to_left == AGENT_STATE_UNKNOWN:
            # Don't turn into perimeter
            # if not (
            #     (self.state.pos_x == self.width and self.state.direction == AGENT_DIRECTION_SOUTH) or
            #     (self.state.pos_y == self.height and self.state.direction == AGENT_DIRECTION_WEST) or
            #     (self.state.pos_x == 1 and self.state.direction == AGENT_DIRECTION_NORTH) or
            #     (self.state.pos_y == 1 and self.state.direction == AGENT_DIRECTION_EAST)
            # ):
            # Stop following route if unknown tiles are found
            if len(self.route) > 0:
                self.route = []
                
            self.state.direction = new_direction_left_right[0]
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT

            # elif info_to_right == AGENT_STATE_UNKNOWN and info_to_forward != AGENT_STATE_UNKNOWN:
            #     self.state.direction = new_direction_left_right[1]
            #     self.state.last_action = ACTION_TURN_RIGHT
            #     return ACTION_TURN_RIGHT

        elif info_to_right == AGENT_STATE_UNKNOWN:
            # Don't turn into perimeter
            # if not (
            #     (self.state.pos_x == self.width and self.state.direction == AGENT_DIRECTION_NORTH) or
            #     (self.state.pos_y == self.height and self.state.direction == AGENT_DIRECTION_EAST) or
            #     (self.state.pos_x == 1 and self.state.direction == AGENT_DIRECTION_SOUTH) or
            #     (self.state.pos_y == 1 and self.state.direction == AGENT_DIRECTION_WEST)
            # ):
            # Stop following route if unknown tiles are found
            if len(self.route) > 0:
                self.route = []
                
            self.state.direction = new_direction_left_right[1]
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
            
        if bump:
            action = ACTION_TURN_LEFT
            direction = new_direction_left_right[0]

            # Turn left or right depending on 
            if info_to_left != AGENT_STATE_WALL:
                self.log("BUMP -> turning left!")
            
            elif info_to_right != AGENT_STATE_WALL:
                self.log("BUMP -> turning right!")
                action = ACTION_TURN_RIGHT
                direction = new_direction_left_right[1]

            self.state.direction = direction
            self.state.last_action = action
            return action

        # If world is "discovered", find closest unknown tile and calculate route
        elif (
            self.width < self.largest_world_dimension and
            self.height < self.largest_world_dimension
        ):
            end_coords = (1, 1)
            manhat = 1000
     
            for y in range(1, self.height):
                for x in range(1, self.width):
                    if (
                        self.state.world[x][y] == AGENT_STATE_UNKNOWN and
                        (abs(self.state.pos_x - x) + abs(self.state.pos_y - y)) < manhat
                    ):
                        manhat = abs(self.state.pos_x - x) + abs(self.state.pos_y - y)
                        end_coords = (x, y)
                        #break

            self.calc_route((self.state.pos_x, self.state.pos_y), end_coords)
            self.state.last_action = ACTION_NOP
            return ACTION_NOP

        else:
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD
