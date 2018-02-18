# SKIPTEST
import curses

import kmp


def compute_prefix(s):
    if not s:
        return ''
    p = kmp.compute_prefix(s)
    return ''.join(
        chr(ord('0') + v + 1) if v < 9 else
        chr(ord('a') + v-9)
        for v in p)


def main(stdscr):
    a, b = '', ''
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, a + b)
        stdscr.addstr(1, 0, compute_prefix(a + b))
        stdscr.move(0, len(a))
        stdscr.refresh()
        c = stdscr.getch()
        if c == 127:  # backspace
            a = a[:-1]
        elif 32 <= c < 127:
            a += chr(c)
        elif c == 11:  # ^K
            b = ''
        elif c == 21:  # ^U
            a = ''
        elif c == curses.KEY_LEFT:
            if a:
                a, b = a[:-1], a[-1] + b
        elif c == curses.KEY_RIGHT:
            if b:
                a, b = a + b[0], b[1:]
        elif c == curses.KEY_HOME:
            a, b = '', a + b
        elif c == curses.KEY_END:
            a, b = a + b, ''
        else:
            raise SystemExit(a + b)


def wrapper():
    stdscr = curses.initscr()
    try:
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        return main(stdscr)
    finally:
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


if __name__ == "__main__":
    wrapper()
