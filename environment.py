from collections import namedtuple
from collections import defaultdict

class Environment:
    def __init__(self):
        self.world_map = defaultdict(list)
        
class Grid_square:
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
