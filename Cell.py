import matplotlib as mpl
maxVel = 127
maxNote = 120


class Cell:
    def __init__(self, x, y):
        self.pos = x, y
        self.pressed = False
        self.note = None
        self.velocity = 0

    def set_note(self, note):
        self.note = note

    def fade(self):
        self.velocity = int(self.velocity * .98)

    def set_velocity(self, velocity):
        self.velocity = velocity
