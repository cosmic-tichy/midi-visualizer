from threading import Thread
import mido
import pygame
from Board import *
from Cell import *
import matplotlib as mpl
import rtmidi

midiout = rtmidi.MidiOut()

available_ports = midiout.get_ports()

print(available_ports)

if available_ports:
    midiout.open_port(3)
else:
    midiout.open_virtual_port("My virtual output")

default_offset = 36


def get_color(val):
    x, y, z, a = mpl.cm.Purples(val)
    x = x * 255
    y = y * 255
    z = z * 255
    return x, y, z


clock = pygame.time.Clock()
pressed = {}
to_be_active_stack = {}
col_background = get_color(0)
col_grid = get_color(0)


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


def main(dimx, dimy, cellsize):
    global to_be_active_stack, pressed
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Midi Visualizer")
    board = Board(dimx, dimy)
    inport = mido.open_input(names[0])

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
        for pos in pressed_copy:
            cell = pressed_copy.get(pos)
            x, y = cell.pos
            pygame.draw.rect(surface, cell.get_color(), (x * cellsize, y * cellsize, cellsize - 1, cellsize - 1))
        to_be_active_copy = to_be_active_stack.copy()
        for pos in to_be_active_copy:
            cell = to_be_active_copy.get(pos)
            x, y = cell.pos
            if cell.velocity < 5:
                to_be_active_stack.pop((x, y))
            else:
                cell.fade()
            pygame.draw.rect(surface, cell.get_color(), (x * cellsize, y * cellsize, cellsize - 1, cellsize - 1))

        pygame.display.update()


if __name__ == "__main__":
    names = mido.get_input_names()
    print(names)
    out_port = mido.open_output()
    main(10, 10, 100)
