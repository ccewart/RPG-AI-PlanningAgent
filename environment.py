class Environment:
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.state = initial_state

    def update_environment(self):
        if not self.game_over(self.state):
            action = 

    def do_action(self, state, action):
        "Override this method to apply an action performed by an agent to a state and return a new state"
        raise NotImplementedError()
    
    def game_over(self, state):
        "Override with terminal states for environment"
        return False

    def percept(self, state):
        return self.state

class RPG_Environment(Environment):
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.state = initial_state

    def update_environment(self):
        if not self.game_over(self.state):
            action = 

    def do_action(self, state, action):
        "Override this method to apply an action performed by an agent to a state and return a new state"
        raise NotImplementedError()
    
    def game_over(self, state):
        "Override with terminal states for environment"
        return False

    def percept(self, state):
        return self.state
       
class Grid_square(RPG_Environment):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.discovered = False
        self.land = False
        self.water = False
        self.wall = False
        self.tree = False
        self.treasure = False
        self.axe = False
        self.key = False
        self.stone = False
        self.door = False
        self.placedStone = False
        self.heuristic = 0
