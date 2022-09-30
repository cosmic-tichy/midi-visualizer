import os.path
import time
from threading import Thread
import mido
import pygame
from mido import MidiFile

import midioutwrapper
from Board import *
from Cell import *
import matplotlib as mpl
import rtmidi
import mido.backends.rtmidi
import inquirer

midiout = rtmidi.MidiOut()

midiWrapper = midioutwrapper.MidiOutWrapper(midiout, 0)

available_ports = midiout.get_ports()
names = mido.get_input_names()

colors = []

color_maps = ['magma', 'viridis', 'inferno', 'cividis', 'plasma',
              'Purples', 'Blues', 'Reds', 'PuBu', 'bone',
              'cool', 'pink', 'copper', 'afmhot', 'gnuplot2',
              'cubehelix', 'gist_earth', 'terrain', 'ocean',
              'prism']

questions = [
    inquirer.List('port',
                  message="Select port number for output to DAW:",
                  choices=available_ports
                  ),
    inquirer.List('instrument',
                  message="Select instrument for capturing MIDI: ",
                  choices=names
                  ),
    inquirer.List('color_map',
                  message="Select color map for visualizer: ",
                  choices=color_maps
                  ),
]
answers = inquirer.prompt(questions)

port_num = available_ports.index(answers['port'])
input_name = answers['instrument']
color_map = answers['color_map']

# port_num = 1
# input_name = 'V49 2'

if available_ports:
    outport = midiout.open_port(port_num)
else:
    midiout.open_virtual_port("My virtual output")

inport = mido.open_input(input_name)

default_offset = 36

clock = pygame.time.Clock()
pressed = {}
to_be_active_stack = {}


def get_color(val, map, glow=False):
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
    a = a * 255

    if glow:
        return x, y, z, 50.0
    else:
        return x, y, z


def get_cell_color(velocity, map):
    vel_perc = velocity / maxVel
    return get_color(vel_perc, map)


def get_cell_glow(velocity, map):
    vel_perc = velocity / maxVel
    return get_color(vel_perc, map, True)


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
            pitch = pressed.get((x, y)).pitchbend
            pressed.pop((x, y))
            note_off = Cell(x, y)
            note_off.active = True
            note_off.set_note(msg.note)
            note_off.set_velocity(vel)
            note_off.pitchbend = pitch
            to_be_active_stack[(x, y)] = note_off
    elif msg.type == 'pitchwheel':
        # print(msg)
        midiWrapper.send_pitch_bend(msg.pitch, msg.channel)
        for note in pressed:
            cell = pressed.get(note)
            cell.set_pitchbend(msg.pitch)
        for note in to_be_active_stack:
            cell = to_be_active_stack.get(note)
            cell.set_pitchbend(msg.pitch)
    elif msg.type == 'control_change':
        midiout.send_message([0xB0, msg.control, msg.value])
        # print(msg)


def read_midi(file, board):
    for msg in MidiFile(file).play():
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
        elif msg.type == 'pitchwheel':
            midiout.send_message([0x14, msg.channel, msg.pitch, msg.time])
            print(msg)
        elif msg.type == 'control_change':
            print(msg)


def init(dimx, dimy):
    cells = np.zeros((dimy, dimx))
    return cells


def main(dimx, dimy, cellsize):
    cell_offset = cellsize - 1
    global to_be_active_stack, pressed, color_map
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Midi Visualizer")
    board = Board(dimx, dimy)

    col_grid = get_color(0, color_map)
    while True:
        clock.tick(120)
        midi = Thread(target=process_midi, args=(inport, board))
        # midi_file = "C:\\Users\\NBMow\\Documents\\projects\\midi-visualizer\\midi_files\\test2 .mid"
        # midi = Thread(target=read_midi, args=(midi_file, board))
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
            pitch_perc = cell.pitchbend / 100
            pitch_scale = (int(cellsize / 2) * pitch_perc) / 1.5
            pitch_offset = (2 * (int(cellsize / 2) * pitch_perc)) / 1.5

            rect_surface = pygame.Surface((cellsize, cellsize))
            rect_surface.set_alpha(100 - (70 * pitch_perc))
            rect_surface.fill(get_cell_color(cell.velocity, color_map))
            surface.blit(rect_surface, ((x * cellsize), (y * cellsize)))

            rect = pygame.draw.rect(surface, (get_cell_color(cell.velocity, color_map)),
                                    ((x * cellsize) + pitch_scale, (y * cellsize) + pitch_scale,
                                     cell_offset - pitch_offset, cell_offset - pitch_offset))

        to_be_active_copy = to_be_active_stack.copy()
        for pos in to_be_active_copy:
            if pos not in keys:
                cell = to_be_active_copy.get(pos)
                x, y = cell.pos
                pitch_perc = cell.pitchbend / 100
                pitch_scale = (int(cellsize / 2) * pitch_perc) / 2
                pitch_offset = (2 * (int(cellsize / 2) * pitch_perc)) / 2
                if cell.velocity < 5:
                    to_be_active_stack.pop((x, y))
                else:
                    cell.fade()
                rect_surface = pygame.Surface((cellsize, cellsize))
                rect_surface.set_alpha(100 - (70 * pitch_perc))
                rect_surface.fill(get_cell_color(cell.velocity, color_map))
                surface.blit(rect_surface, ((x * cellsize), (y * cellsize)))

                rect = pygame.draw.rect(surface, get_cell_color(cell.velocity, color_map),
                                        ((x * cellsize) + pitch_scale, (y * cellsize) + pitch_scale,
                                         cell_offset - pitch_offset, cell_offset - pitch_offset))

        pygame.display.update()


if __name__ == "__main__":
    # color_map = input("input color map name from list above: ")
    main(10, 10, 100)
