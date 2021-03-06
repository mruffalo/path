# PATH interpreter
# Copyright (c) 2003-04 Francis Rogers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import os

class Path:
    """Implementation of the PATH programming language in Python."""

    # This class uses the following data attributes:
    # x: current x position
    # y: current y position
    # p: current memory cell pointer
    # d: current direction
    # s: whether the next cell is being skipped
    # mem: array of memory cells
    # prog: 2-dimensional array of characters that make up the program
    # plugins: array of plug-in objects for the interpreter to use
    # func_in: function to use for input
    # func_out: function to use for output
    # plug_lock: plugin the interpreter is locked on
    # verbose: if true, enable debug messages

    def __init__(self):
        """Initialize the class."""
        self.PATH_DIRECTION_RIGHT = 1
        self.PATH_DIRECTION_DOWN = 2
        self.PATH_DIRECTION_LEFT = 3
        self.PATH_DIRECTION_UP = 4

        self.func_in = sys.stdin.read
        self.func_out = sys.stdout.write
        self.plug_lock = None

        self.plugins = []

    def __add__(self, x):
        """Step thru x symbols. Return false if end of program encountered."""
        ret = 0
        for i in range(x):
            ret = self.step()
            if not ret:
                return ret
        return ret

    def addplugin(self, plugin):
        """This method is called internally by plugins.

        (To add a plugin to the interpreter: 'execfile(plugin, {"glob_path":prog})') """
        self.plugins.append(plugin)

    def debug(self, msg):
        """Print a debug message."""
        if self.verbose:
            self.errprint("({},{}) {}".format(self.x, self.y, msg))

    def dir2string(self, d):
        """Get the string representation of a direction id."""
        if d == self.PATH_DIRECTION_RIGHT:
            return "right"
        elif d == self.PATH_DIRECTION_DOWN:
            return "down"
        elif d == self.PATH_DIRECTION_LEFT:
            return "left"
        elif d == self.PATH_DIRECTION_UP:
            return "up"

    def errprint(self, msg):
        """Print a message to stderr."""
        sys.stderr.write(os.path.basename(sys.argv[0]) + ": " + msg + "\n")

    def normalize_line_length(self):
        if any(len(l) for l in self.prog):
            longest = max(len(l) for l in self.prog)
            for l in range(len(self.prog)):
                # "{:{}}" works as a format string too, but I prefer
                # using explicit indices when nesting fields
                self.prog[l] = '{0:{1}}'.format(self.prog[l], longest)

    def load_prog_file(self, filename):
        """Load a new program file into the interpreter."""
        try:
            with open(filename) as f:
                self.prog = f.readlines()
            if self.prog[0].startswith("#!"):
                self.prog = self.prog[1:]

            self.normalize_line_length()
        except IOError:
            self.errprint("can't open file '{}'".format(filename))
            sys.exit(1)
        self.reset()

    def load_prog_array(self, progarray):
        """Load a new program directly into the interpreter."""
        self.prog = progarray
        self.normalize_line_length()
        self.reset()

    def lock(self, plugin):
        """Lock the interpreter on a specific plugin. (Use path.lock(None) to unlock.)"""
        self.plug_lock = plugin

    def redefine_io(self, infunc, outfunc):
        """Redefine the input and output functions used by the , and . symbols.

        (Defaults are sys.stdin.read for input and sys.stdout.write for output."""
        self.func_in = infunc
        self.func_out = outfunc

    def reset(self):
        """Reset the program state and restart the program."""
        self.x = 0
        self.y = 0
        self.p = 0
        self.d = self.PATH_DIRECTION_RIGHT
        self.s = False
        self.mem = [0]
        self.verbose = False

        for ny in range(len(self.prog)):
            for nx in range(len(self.prog[ny])):
                if self.prog[ny][nx] == '$':
                    self.y = ny
                    self.x = nx

    def run(self):
        """Run the entire program."""
        while not self.step():
            pass

    def runplugins(self):
        """Run all the loaded plugins on the current symbol."""
        for plugin in self.plugins:
            if not plugin.call(self):
                return False
        return True

    def step(self):
        """
        Step through a single symbol of the program.

        Returns True if end of program encountered, False if
        another step should be executed.
        """
        cursym = self.prog[self.y][self.x]

        if self.s:
            self.s = False
        elif self.plug_lock is not None:
            self.plug_lock.call(self)
        elif not self.runplugins():
            pass
        elif cursym == '$':
            self.debug("Start")
        elif cursym == '#':
            self.debug("End")
            return True
        elif cursym == '!':
            self.s = True
            self.debug("Skip next symbol")
        elif cursym == '}':
            self.p += 1
            if self.p > len(self.mem) - 1:
                self.mem.append(0)
            self.debug("New memory cell: {}".format(self.p))
        elif cursym == '{':
            if self.p > 0:
                self.p -= 1
            self.debug("New memory cell: {}".format(self.p))
        elif cursym == '/':
            if self.d == self.PATH_DIRECTION_RIGHT:
                self.d = self.PATH_DIRECTION_UP
            elif self.d == self.PATH_DIRECTION_DOWN:
                self.d = self.PATH_DIRECTION_LEFT
            elif self.d == self.PATH_DIRECTION_LEFT:
                self.d = self.PATH_DIRECTION_DOWN
            elif self.d == self.PATH_DIRECTION_UP:
                self.d = self.PATH_DIRECTION_RIGHT
            self.debug("New direction: {}".format(self.dir2string(self.d)))
        elif cursym == '\\':
            if self.d == self.PATH_DIRECTION_RIGHT:
                self.d = self.PATH_DIRECTION_DOWN
            elif self.d == self.PATH_DIRECTION_DOWN:
                self.d = self.PATH_DIRECTION_RIGHT
            elif self.d == self.PATH_DIRECTION_LEFT:
                self.d = self.PATH_DIRECTION_UP
            elif self.d == self.PATH_DIRECTION_UP:
                self.d = self.PATH_DIRECTION_LEFT
            self.debug("New direction: {}".format(self.dir2string(self.d)))
        elif cursym == '>':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_RIGHT
                self.debug("New direction: {}".format(self.dir2string(self.d)))
        elif cursym == 'v':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_DOWN
                self.debug("New direction: {}".format(self.dir2string(self.d)))
        elif cursym == '<':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_LEFT
                self.debug("New direction: {}".format(self.dir2string(self.d)))
        elif cursym == '^':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_UP
                self.debug("New direction: {}".format(self.dir2string(self.d)))
        elif cursym == '+':
            self.mem[self.p] += 1
            if self.mem[self.p] == 256:
                self.mem[self.p] = 0
            self.debug("Incremented memory cell {} to {}".format(self.p, self.mem[self.p]))
        elif cursym == '-':
            self.mem[self.p] -= 1
            if self.mem[self.p] == -1:
                self.mem[self.p] = 255
            self.debug("Decremented memory cell {} to {}".format(self.p, self.mem[self.p]))
        elif cursym == ',':
            self.mem[self.p] = ord(self.func_in(1))
            self.debug("Inputted {} to memory cell {}".format(self.mem[self.p], self.p))
        elif cursym == '.':
            self.func_out(chr(self.mem[self.p]))
            self.debug("Outputted {} from memory cell {}".format(self.mem[self.p], self.p))

        if self.d == self.PATH_DIRECTION_RIGHT:
            self.x += 1
        elif self.d == self.PATH_DIRECTION_DOWN:
            self.y += 1
        elif self.d == self.PATH_DIRECTION_LEFT:
            self.x -= 1
        elif self.d == self.PATH_DIRECTION_UP:
            self.y -= 1
        try:
            self.prog[self.y][self.x]
            if self.x < 0:
                raise IndexError
            if self.y < 0:
                raise IndexError
        except IndexError:
            self.debug("Ran off the side")
            return True

        return False
