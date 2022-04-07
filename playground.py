import pathlib

from pygame import QUIT, KEYDOWN

from parsing.bufferio import StringContainer, FileContainer
from parsing.commander import Commander
from parsing.lexer import Lexer
from parsing.parser import AST
from turing.environment import TheTape
from turing.machine import TuringMachine

import pygame
import pygame_menu

from typing import Tuple
import sys


pygame.init()


def set_text(string, coordx, coordy, fontSize, color: Tuple[int, int, int] = (255, 255, 255)):
    # Function to set text
    font = pygame.font.Font('freesansbold.ttf', fontSize)
    # (0, 0, 0) is black, to make black text
    text = font.render(string, True, color)
    textRect = text.get_rect()
    textRect.center = (coordx, coordy)
    return text, textRect


def display_tape(screen: pygame.display, tape: TheTape, machine: TuringMachine):
    x, y = screen.get_size()
    window_size = (x // 11) if x % 11 > 0 else (x // 11 - 1)  # how many blocks of the tape we can show

    screen.fill((255, 255, 255))

    xstart = 0
    if len(tape) < window_size:
        # We can display the whole tape
        dtape = tape.memory
        xstart = (x - ((len(tape) * 11) + 1)) >> 1
    else:
        # We need to display a window of the tape
        win_mid = window_size >> 1
        start = 0 if tape[machine] < win_mid else (tape[machine] - win_mid)
        dend = len(tape) - (tape[machine] + 1)
        end = -1 if dend < win_mid else (dend - win_mid + (win_mid % 2) + 1)
        if end < 0:
            dtape = tape.memory[start:]
        else:
            dtape = tape.memory[start:end]

    tape_start = int(y * 0.8)
    for ci, c in enumerate(dtape):
        screen_index = 11 * ci + xstart
        img, rect = set_text(c, screen_index + 5, tape_start + 5, 10)
        screen.fill((0, 0, 0), (screen_index, tape_start, 10, 10))
        screen.blit(img, rect)

    pointer = tape[machine]
    img, rect = set_text('v', 11 * pointer + 5 + xstart, tape_start - 5, 10, (0, 0, 0))
    screen.blit(img, rect)

    pygame.display.update()
    pass


def main():
    test = """
    print_name:
    {
    write 'A';
    right 1;write 'a';
    right 1;write 'r';
    right 1;write 'o'; 
    right 1;write 'n';
    right 1;
    }
    goto print_name;
    right 5;
    left 20;
    goto print_name;
    while(= read '0') { write '1'; right 1; }
    halt;
    """

    screen = pygame.display.set_mode((640, 480))

    tape = TheTape()
    machine = TuringMachine(tape)

    fname = ''

    def initialize_tape(value):
        tape.initialize_tape(value)

    def initialize_filename(value):
        global fname
        fname = pathlib.Path(value)

    def run_simulation():
        tape.reset(True)

        code = AST(Lexer(StringContainer(test) if len(str(fname)) == 0 else FileContainer(fname)))
        code.build_tree()

        commander = Commander(code)
        while commander.has_next():
            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN):
                    sys.exit()
            commander.run_next(machine)
            display_tape(screen, tape, machine)
            pygame.time.delay(100)

    main_menu = pygame_menu.Menu('Pause', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
    tape_entry = pygame_menu.Menu('Change Tape', 400, 300, theme=pygame_menu.themes.THEME_BLUE)
    file_entry = pygame_menu.Menu('Change File', 400, 300, theme=pygame_menu.themes.THEME_BLUE)

    file_entry.add.label('File (Leave empty for sample):', max_char=25)
    file_entry.add.text_input('', onchange=initialize_filename)
    file_entry.add.button('Okay', pygame_menu.events.BACK)

    tape_entry.add.label('Initial Tape State:')
    tape_entry.add.text_input('', onchange=initialize_tape)
    tape_entry.add.button('Okay', pygame_menu.events.BACK)

    main_menu.add.button('Run', run_simulation)
    main_menu.add.button('Change Tape', tape_entry)
    main_menu.add.button('Change Code', file_entry)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)

    main_menu.mainloop(screen)


if __name__ == '__main__':
    main()

