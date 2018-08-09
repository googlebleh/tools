#!/usr/bin/python3

import time
import curses


def main(stdscr):
    # Clear screen
    stdscr.clear()

        for i in range(0, 10):
            v = i-10
            if i:
                stdscr.move(0, 0)
                stdscr.deleteln()
            #  stdscr.addstr(i, 0, '10 divided by {} is {}\n'.format(v, 10/v))
            stdscr.addstr('10 divided by {} is {}\n'.format(v, 10/v))
            stdscr.refresh()

            stdscr.getkey()

    stdscr.addstr("hi\n")
    stdscr.addstr("my name is joe\n")
    stdscr.addstr("i work in a button factory\n")
    stdscr.refresh()
    time.sleep(1)


if __name__ == "__main__":
    curses.wrapper(main)
