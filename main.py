from threading import Thread
import mido
import pygame
from Board import *
from Cell import *
import matplotlib as mpl
import rtmidi
import mido.backends.rtmidi

midiout = rtmidi.MidiOut()

available_ports = midiout.get_ports()

print(available_ports)

if available_ports:
    midiout.open_port(2)
else:
    midiout.open_virtual_port("My virtual output")


names = mido.get_input_names()
print(names)
out_port = mido.open_output()
inport = mido.open_input(names[1])

default_offset = 36
clock = pygame.time.Clock()
pressed = {}
to_be_active_stack = {}


def get_color(val, map):
    if map == "magma":
        x, y, z, a = mpl.cm.magma(val)
    elif map == "viridis":
        x, y, z, a = mpl.cm.viridis(val)
    elif map == "inferno":
        x, y, z, a = mpl.cm.inferno(val)
    elif map == "cividis":
        x, y, z, a = mpl.cm.cividis(val)
    elif map == "plasma":
        x, y, z, a = mpl.cm.plasma(val)
    elif map == "Purples":
        x, y, z, a = mpl.cm.Purples(val)
    elif map == "Blues":
        x, y, z, a = mpl.cm.Blues(val)
    elif map == "Reds":
        x, y, z, a = mpl.cm.Reds(val)
    elif map == "PuBu":
        x, y, z, a = mpl.cm.PuBu(val)
    elif map == "bone":
        x, y, z, a = mpl.cm.bone(val)
    elif map == "cool":
        x, y, z, a = mpl.cm.cool(val)
    elif map == "pink":
        x, y, z, a = mpl.cm.pink(val)
    elif map == "copper":
        x, y, z, a = mpl.cm.copper(val)
    elif map == "afmhot":
        x, y, z, a = mpl.cm.afmhot(val)
    elif map == "gnuplot2":
        x, y, z, a = mpl.cm.gnuplot2(val)
    elif map == "cubehelix":
        x, y, z, a = mpl.cm.cubehelix(val)
    elif map == "gist_earth":
        x, y, z, a = mpl.cm.gist_earth(val)
    elif map == "terrain":
        x, y, z, a = mpl.cm.terrain(val)
    elif map == "ocean":
        x, y, z, a = mpl.cm.ocean(val)
    elif map == "prism":
        x, y, z, a = mpl.cm.prism(val)
    else:
        x, y, z, a = mpl.cm.magma(val)

    x = x * 255
    y = y * 255
    z = z * 255
    return x, y, z


def get_cell_color(velocity, map):
    vel_perc = velocity / maxVel
    return get_color(vel_perc, map)


def process_midi(inport, board):
    msg = inport.receive()
    global pressed, to_be_active_stack
    if msg.type == 'note_on':
        midiout.send_message([0x90, msg.note, msg.velocity])
        positions = board.get_pos_with_note(msg.note)
        for pos in positions:
            x, y = pos
            note_on = Cell(x, y)
            note_on.active = False
            note_on.set_note(msg.note)
            note_on.set_velocity(msg.velocity)
            pressed[(x, y)] = note_on
    elif msg.type == 'note_off':
        midiout.send_message([0x80, msg.note, msg.velocity])
        positions = board.get_pos_with_note(msg.note)
        for pos in positions:
            x, y = pos
            vel = pressed.get((x, y)).velocity
            pressed.pop((x, y))
            note_off = Cell(x, y)
            note_off.active = True
            note_off.set_note(msg.note)
            note_off.set_velocity(vel)
            to_be_active_stack[(x, y)] = note_off


def init(dimx, dimy):
    cells = np.zeros((dimy, dimx))
    return cells


def main(dimx, dimy, cellsize, color_map):
    global to_be_active_stack, pressed
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Midi Visualizer")
    board = Board(dimx, dimy)

    col_grid = get_color(0, color_map)
    while True:
        clock.tick(120)
        midi = Thread(target=process_midi, args=(inport, board))
        midi.start()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                midi.join()
                return

        surface.fill(col_grid)
        pressed_copy = pressed.copy()
        keys = []
        for pos in pressed_copy:
            cell = pressed_copy.get(pos)
            keys.append(pos)
            x, y = cell.pos
            pygame.draw.rect(surface, get_cell_color(cell.velocity, color_map),
                             (x * cellsize, y * cellsize, cellsize, cellsize))
        to_be_active_copy = to_be_active_stack.copy()
        for pos in to_be_active_copy:
            if pos not in keys:
                cell = to_be_active_copy.get(pos)
                x, y = cell.pos
                if cell.velocity < 5:
                    to_be_active_stack.pop((x, y))
                else:
                    cell.fade()
                pygame.draw.rect(surface, get_cell_color(cell.velocity, color_map),
                                 (x * cellsize, y * cellsize, cellsize, cellsize))

        pygame.display.update()


if __name__ == "__main__":
    color_maps = [('magma', 1), ('viridis', 2), ('inferno', 3), ('cividis', 4), ('plasma', 5),
                  ('Purples', 6), ('Blues', 7), ('Reds', 8), ('PuBu', 9), ('bone', 10),
                  ('cool', 11), ('pink', 12), ('copper', 13), ('afmhot', 14), ('gnuplot2', 15),
                  ('cubehelix', 16), ('gist_earth', 17), ('terrain', 18), ('ocean', 19),
                  ('prism', 20)]
    for color in color_maps:
        print(color[0])
    color_map = input("input color map name from list above: ")
    main(10, 10, 100, color_map)
