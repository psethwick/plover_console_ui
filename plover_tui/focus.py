from os import system
from time import sleep

TUI_MARKER = "plover_tui"
PLACE_MARKER = "_where_we_were"


def mark(mark):
    system(f'i3-msg mark add {mark}')
    sleep(.01)


def focus_tui():
    mark(PLACE_MARKER)
    system(f'i3-msg "[con_mark={TUI_MARKER}] focus"')
    sleep(.01)


def focus_pop():
    system(f'i3-msg "[con_mark={PLACE_MARKER}] focus"')
    sleep(.01)
