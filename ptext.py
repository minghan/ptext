#!/usr/bin/env python

"""

===== General Information =====
  
  ptext is a text-based presenter written in python.
  ptext is written by minghan licensed under the MIT license.

  See README for more information.

===== Credit =====

  I have found the following documents helpful:

  * http://heather.cs.ucdavis.edu/~matloff/Python/PyCurses.pdf
  * http://docs.python.org/library/curses.html

"""

import curses, sys, traceback


class Slide:
    def __init__(self, title, body=[]):
        self.title = title
        self.body = body

class Settings:
    NEXT = ['n']
    BACK = ['b','p']
    QUIT = ['q', 27]

    TITLE_PREFIX = '+'
    POINT_PREFIX = '-'


class Messages:
    FIRST_SLIDE = "[Start of Presentation]"
    LAST_SLIDE = "[End of Presentation]"


# Don't want to pollute the real global namespace
class Globals:
    screen = None
    slides = []
    filename = None


def init_screen():
    Globals.screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()

    # (fg, bg) 
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Apparently, I can't hide the cursor (for now...)
    # http://www.technovelty.org/linux/term.html
    #curses.curs_set(1)  # 0, 1, or 2, for invisible, normal, or very visible

def restore_screen():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def centerize():
    maxy, maxx = Globals.screen.getmaxyx()

def load_slide(n):
    """
    Load the n^th slide
    """
    Globals.screen.clear()
    
    if n <= 0:
        n = 0
        Globals.screen.addstr(0, 0, Messages.FIRST_SLIDE)
    elif n > len(Globals.slides):
        n = len(Globals.slides) + 1
        Globals.screen.addstr(0, 0, Messages.LAST_SLIDE)
    else:
        Globals.screen.addstr(0, 0, Globals.slides[n-1].title)
        y = 2
        for line in Globals.slides[n-1].body:
            newline = "* %s" % line
            Globals.screen.addstr(y, 0, newline)
            y = y + 1

    Globals.screen.refresh()

    return n

def parse_file(f):
    """
    @param f Pointer to file object
    """

    def reset_attrib():
        """
        @return Default values for (title, body, point)
        """
        return ("", [], "")
    
    is_first_slide = True
    title, body, point = reset_attrib()

    for line in f:
        line = line.rstrip()
        if line == "":
            continue
        elif line.startswith(Settings.TITLE_PREFIX):
            if not is_first_slide:
                if not is_first_point:
                    body.append(point)
                Globals.slides.append(Slide(title, body))
                title, body, point = reset_attrib()
            else:
                is_first_slide = False
            title = line.lstrip(Settings.TITLE_PREFIX + ' ')
            is_first_point = True
        elif line.startswith(Settings.POINT_PREFIX):
            if not is_first_point:
                body.append(point)
                point = ""
            else:
                is_first_point = False
            point = line.lstrip(Settings.POINT_PREFIX)
        else:
            point += "\n%s" % line

    if not is_first_point:
        body.append(point)

    if not is_first_slide:
        Globals.slides.append(Slide(title, body))


def load_file():
    # get the file name
    try:
        Globals.filename = sys.argv[1]
    except IndexError:
        print "Usage: %s [FILE]" % (sys.argv[0])
        sys.exit(2) # 2 for command line syntax errors

    # load the file
    try:
        f = open(Globals.filename)
    except IOError:
        print "%s: %s: No such file or directory" % (sys.argv[0], sys.argv[1])
        sys.exit(2)

    parse_file(f)
 
    f.close()


def main():
    load_file()


    init_screen()

    n = 0

    load_slide(n)

    try:
        while True:
            c = chr(Globals.screen.getch())
            if c in Settings.QUIT:
                break
            elif c in Settings.NEXT:
                n = load_slide(n + 1)
            elif c in Settings.BACK:
                n = load_slide(n - 1)

    except Exception:
        restore_screen()
        traceback.print_exc()


    restore_screen()


if __name__ == '__main__':
    main()

