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
        self.velocity = int(self.velocity * .95)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def get_color(self):
        vel_perc = self.velocity / maxVel
        x, y, z, a = mpl.cm.Purples(vel_perc)
        x = x * 255
        y = y * 255
        z = z * 255
        return x, y, z
