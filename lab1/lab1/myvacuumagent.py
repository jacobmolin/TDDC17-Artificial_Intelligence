import sys
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
class MyVacuumAgent(Agent):

    def __init__(self, world_width, world_height, log):
        super().__init__(self.execute)
        self.initial_random_actions = 10
        self.iteration_counter = world_width * world_height * 2
        self.state = MyAgentState(world_width, world_height)
        self.log = log
        self.tiles_visited = 0
        self.tiles_amount = sys.maxsize
        self.width = sys.maxsize / 2
        self.height = sys.maxsize / 2
        self.way_home = []
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


    def in_corner(self):
        return (
            (self.state.pos_x == 1 and self.state.pos_y == 1) or
            (self.state.pos_x == 1 and self.state.pos_y == self.height) or
            (self.state.pos_x == self.width and self.state.pos_y == 1) or
            (self.state.pos_x == self.width and self.state.pos_y == self.height)
        )
                

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

        if self.state.world[self.state.pos_x][self.state.pos_y] == AGENT_STATE_UNKNOWN:
            self.tiles_visited += 1

        # Log info 
        self.log('value at pos: {}'.format(self.state.world[self.state.pos_x][self.state.pos_y]))
        self.log('tiles visited: {}'.format(self.tiles_visited))

        # Updating world
        if bump:
            # Get an xy-offset pair based on where the agent is facing
            #          NORTH    EAST   SOUTH     WEST
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]
            offset_x = self.state.pos_x + offset[0]
            offset_y = self.state.pos_y + offset[1]
            
            if self.state.world[offset_x][offset_y] == AGENT_STATE_UNKNOWN:
                self.tiles_visited += 1

            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(offset_x, offset_y, AGENT_STATE_WALL)

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
            
            
            self.tiles_amount = (self.width + 2) * (self.height + 2) - 4
            
        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        elif home:  
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_HOME)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)

        # Debug
        self.state.print_world_debug()

        # Check where can go
        # Get an xy-offset pair to the left, to the right and forward based on where the agent is facing
        offset_l_r_f = [
                            [(-1, 0), (1, 0), (0, -1)],
                            [(0, -1), (0, 1), (1, 0)],
                            [(1, 0), (-1, 0), (0, 1)],
                            [(0, 1), (0, -1), (-1, 0)]
                        ][self.state.direction]
                                
        # A pair containing information about whats to the left and to the right
        info_to_left = self.state.world[self.state.pos_x + (offset_l_r_f[0])[0]][self.state.pos_y + (offset_l_r_f[0])[1]]
        info_to_right = self.state.world[self.state.pos_x + (offset_l_r_f[1])[0]][self.state.pos_y + (offset_l_r_f[1])[1]]
        info_to_forward = self.state.world[self.state.pos_x + (offset_l_r_f[2])[0]][self.state.pos_y + (offset_l_r_f[2])[1]]

        # Get direction pair to the left and right of agent
        new_direction_left_right = [
                                    (AGENT_DIRECTION_WEST, AGENT_DIRECTION_EAST),
                                    (AGENT_DIRECTION_NORTH, AGENT_DIRECTION_SOUTH),
                                    (AGENT_DIRECTION_EAST, AGENT_DIRECTION_WEST),
                                    (AGENT_DIRECTION_SOUTH, AGENT_DIRECTION_NORTH)
                                ][self.state.direction]

        self.log("tiles left: {}".format((self.tiles_amount - self.tiles_visited - 1)))
        self.log("width: {}".format(self.width))
        self.log("height: {}".format(self.height))

        # Decide action
        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK

        # All tiles visited
        if (self.tiles_amount - self.tiles_visited - 1) == 0:
            if home:
                # Stop at Home-tile if whole world is updated
                self.iteration_counter = 0
                self.log("Parked at home!")
                self.state.last_action = ACTION_NOP
                return ACTION_NOP
            
            # Calculate way home
            elif len(self.way_home) == 0:
                home = (1, 1)
                for y in range(self.state.world_height):
                    for x in range(self.state.world_width):
                        if self.state.world[x][y] == AGENT_STATE_HOME:
                            home = (x, y)

                # Steps to home in x- and y-direction
                amount_steps_x = abs(home[0] - self.state.pos_x)
                amount_steps_y = abs(home[1] - self.state.pos_y)

                # Decide action to turn agent in right direction for going in x-direction
                if amount_steps_x > 0:
                    if home[0] < self.state.pos_x:
                        if self.state.direction == AGENT_DIRECTION_NORTH:
                            self.way_home.extend([ACTION_TURN_LEFT])
                        elif self.state.direction == AGENT_DIRECTION_EAST:
                            self.way_home.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT])
                        elif self.state.direction == AGENT_DIRECTION_SOUTH:
                            self.way_home.extend([ACTION_TURN_RIGHT])
                    else:
                        if self.state.direction == AGENT_DIRECTION_NORTH:
                            self.way_home.extend([ACTION_TURN_RIGHT])
                        elif self.state.direction == AGENT_DIRECTION_WEST:
                            self.way_home.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT])
                        elif self.state.direction == AGENT_DIRECTION_SOUTH:
                            self.way_home.extend([ACTION_TURN_LEFT])

                    self.way_home.extend([ACTION_FORWARD]*amount_steps_x)

                # Decide action to turn agent in right direction for going in y-direction
                if amount_steps_y > 0:
                    if home[1] < self.state.pos_y:
                        if amount_steps_x > 0 or self.state.direction == AGENT_DIRECTION_WEST:
                            self.way_home.extend([ACTION_TURN_RIGHT])
                        elif self.state.direction == AGENT_DIRECTION_EAST:
                            self.way_home.extend([ACTION_TURN_LEFT])
                        elif self.state.direction == AGENT_DIRECTION_SOUTH:
                            self.way_home.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT])
                    else:
                        if amount_steps_x > 0 or self.state.direction == AGENT_DIRECTION_EAST:
                            self.way_home.extend([ACTION_TURN_RIGHT])
                        elif self.state.direction == AGENT_DIRECTION_WEST:
                            self.way_home.extend([ACTION_TURN_LEFT])
                        elif self.state.direction == AGENT_DIRECTION_NORTH:
                            self.way_home.extend([ACTION_TURN_LEFT, ACTION_TURN_LEFT])

                    self.way_home.extend([ACTION_FORWARD]*amount_steps_y)
            
            # If a way home, follow it
            if len(self.way_home) > 0:
                self.log("Way home: {}".format(self.way_home))
                action = self.way_home.pop(0)
                if action == ACTION_TURN_LEFT:
                    self.state.direction = new_direction_left_right[0]
                elif action == ACTION_TURN_RIGHT:
                    self.state.direction = new_direction_left_right[1]

                self.state.last_action = action
                return action

        # Determine coordinates to the left and to the right of agent's position
        coords_to_left = (self.state.pos_x + (offset_l_r_f[0])[0], self.state.pos_y + (offset_l_r_f[0])[1])
        coords_to_right = (self.state.pos_x + (offset_l_r_f[1])[0], self.state.pos_y + (offset_l_r_f[1])[1])
        
        # Determine if to go to forward or turn left/right
        # Home-tile is just passed
        if info_to_forward == AGENT_STATE_UNKNOWN or info_to_forward == AGENT_STATE_HOME:
            if (
                # Along perimeter?
                info_to_left == AGENT_STATE_UNKNOWN and
                (coords_to_left[0] < 1 or coords_to_left[0] > self.width or
                coords_to_left[1] < 1 or coords_to_left[1] > self.height)
            ):
                self.state.direction = new_direction_left_right[0]
                self.state.last_action = ACTION_TURN_LEFT
                return ACTION_TURN_LEFT

            elif (
                # Along perimeter?
                info_to_right == AGENT_STATE_UNKNOWN and
                not self.in_corner() and
                (coords_to_right[0] < 1 or coords_to_right[0] > self.width or
                coords_to_right[1] < 1 or coords_to_right[1] > self.height)
            ):
                self.state.direction = new_direction_left_right[1]
                self.state.last_action = ACTION_TURN_RIGHT
                return ACTION_TURN_RIGHT

            else:
                self.state.last_action = ACTION_FORWARD
                return ACTION_FORWARD

        elif info_to_right == AGENT_STATE_UNKNOWN or info_to_right == AGENT_STATE_HOME:
            self.state.direction = new_direction_left_right[1]
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
    
        elif info_to_left == AGENT_STATE_UNKNOWN or info_to_left == AGENT_STATE_HOME:
            self.state.direction = new_direction_left_right[0]
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT

        # Turn if bumping in to wall 
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
        else:
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD
