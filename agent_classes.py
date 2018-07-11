class Coords():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def get(self):
        return (self.x, self.y)

class Compass():
    def __init__(self):
        self.orient_index = 0
        self.cardinals = ['N', 'E', 'S', 'W']

    def rotate(self, direction):
        self.orient_index = (self.orient_index - 1) % 4 if direction == 'l' else self.orient_index
        self.orient_index = (self.orient_index + 1) % 4 if direction == 'r' else self.orient_index
    
    @property
    def get(self):
        return self.cardinals[self.orient_index]

class Character():
    def __init__(self, x, y):
        self.coordinates = Coords(x, y)
        self.curr_dir = Compass()

    def move_forward(self):
        self.coordinates.y += 1 if self.curr_dir.get == 'N' else 0
        self.coordinates.x += 1 if self.curr_dir.get == 'E' else 0
        self.coordinates.y -= 1 if self.curr_dir.get == 'S' else 0
        self.coordinates.x -= 1 if self.curr_dir.get == 'W' else 0
        
    def rotate(self, direction):
        self.curr_dir.rotate(direction)
    
    @property
    def get_orientation(self):
        return self.curr_dir.get
    
    @property
    def get_position(self):
        return self.coordinates.get

        

