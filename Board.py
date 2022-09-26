import math
from Cell import *
import numpy as np
import array as arr

startOctave = 36
endOctave = 84
centerGridSize = 7
col_background = (10, 10, 40)


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = {}
        self.note_map = [[] for _ in range(25)]
        for y in range(height):
            if y >= int(height/2):
                note = ((int(height) - 1) - y) * int(height/2)
            else:
                note = (int(height / 2) * y)
            for x in range(width):
                if x >= int(width / 2):
                    note = note - 1
                cell = Cell(x, y)
                self.cells[(x, y)] = cell
                self.note_map[note].append((x, y))
                if x < int(width/2):
                    note = note + 1

    def get_pos_with_note(self, note):
        return self.note_map[note % 25]

    def get_neighbors(self, cell):
        n = []
        r, c = cell.pos
        n.append(self.cells[(r - 1) % self.y, (c - 1) % self.x])
        n.append(self.cells[(r - 1) % self.y, c])
        n.append(self.cells[(r - 1) % self.y, (c + 1) % self.x])
        n.append(self.cells[r, (c - 1) % self.x])
        n.append(self.cells[r, (c + 1) % self.x])
        n.append(self.cells[(r + 1) % self.y, (c - 1) % self.x])
        n.append(self.cells[(r + 1) % self.y, c])
        n.append(self.cells[(r + 1) % self.y, (c + 1) % self.x])
        return n