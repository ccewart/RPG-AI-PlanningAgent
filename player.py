class Player:
    def __init__(self, env):
        """set up the agent"""
        self.env = env

    def go(self, n):
        """acts for n time steps"""
        raise NotImplementedError
        

class World_Model(Player):
    def __init__(self, initial_state):
        """initialise environment"""
        self.initial_state = initial_state
        self.state = initial_state
        self.worldMap = [[Grid_square(x, y) for x in range(160)] for y in range(160)]

    #def update_environment(self):
        #if not self.game_over(self.state):
            #action = 

    def do_action(self, state, action):
        "Override this method to apply an action performed by an agent to a state and return a new state"
        raise NotImplementedError()

    def percept(self, state):
        return self.state

