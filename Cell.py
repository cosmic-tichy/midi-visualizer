import math

import matplotlib as mpl

maxVel = 127
maxNote = 120
maxPitch = 8191
minPitch = -8191


class Cell:
    def __init__(self, x, y):
        self.pos = x, y
        self.pressed = False
        self.note = None
        self.velocity = 0
        self.pitchbend = 0

    def set_note(self, note):
        self.note = note

    def fade(self):
        self.velocity = int(self.velocity * .98)
        self.pitchbend = int(self.pitchbend * .98)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_pitchbend(self, val):
        pitch = abs(val)
        self.pitchbend = int((pitch / maxPitch) * 100)
