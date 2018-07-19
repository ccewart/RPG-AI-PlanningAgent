class Environment():
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.state = initial_state

    def do_action(self, state, action):
        "Override this method to apply an action performed by an agent to a state and return a new state"
        raise NotImplementedError()

class AI_Environment(Environment):
    def do_action(self, state, action):
        print(f'do {action} on {state}')


worldModel = AI_Environment('state')
worldModel.do_action('abc', 'f')


class Parent(object):
    def __init__(self):
        self.value = 5

    def get_value(self):
        return self.value

class Child(Parent):
    pass

c = Child()
print(c.get_value())

