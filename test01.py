from environment import *

Map = Environment()
Grid_square = namedtuple('Grid_square', 'coords discovered land water wall tree treasure axe key stone heuristic')
coord = Grid_square(coords = (1,1), land = 'True', discovered = 'True')
