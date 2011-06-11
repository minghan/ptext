#!/usr/bin/python

"""

===== INFO =====
  
  ptext is a text-based presenter written in python

===== MIT LICENSE =====

  Copyright (C) 2011 by Ming Han Teh (teh_minghan@hotmail.com)

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.


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
            title = line.lstrip(Settings.TITLE_PREFIX)
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

    # (fg, bg) 
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

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

