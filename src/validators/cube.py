class AbstractRubikCube(object):
    def __init__(self):
        self.cube = self.create_cube()

    def turn(self):
        pass

    def turns(self):
        pass
    
    def create_cube(self):
        pass

    def is_solved(self):
        pass

    def is_valid(self):
        pass
    