#!/usr/bin/env python
#
# PATH Interpreter v0.3
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

class path:
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
    # verbose: if true, enable debug messages

    
    def __init__(self):
        """Initialize the class."""
        self.PATH_DIRECTION_RIGHT = 1
        self.PATH_DIRECTION_DOWN = 2
        self.PATH_DIRECTION_LEFT = 3
        self.PATH_DIRECTION_UP = 4
        
        self.plugins = []

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

    def addplugin(self, plugin):
        """This method is called internally by plugins.

        (To add a plugin to the interpreter: 'execfile(plugin, {"glob_path":prog})') """
        self.plugins.append(plugin)

    def errprint(self, msg):
        """Print a message to stderr."""
        sys.stderr.write(os.path.basename(sys.argv[0]) + ": " + msg + "\n")

    def loadfile(self, filename):
        """Load a program into the interpreter."""
        try:
            file = open(filename, 'r')
            self.prog = file.readlines()
            if self.prog[0][0:2] == "#!":
                self.prog = self.prog[1:]

            longest = 0
            for l in self.prog:
                if len(l) > longest:
                    longest = len(l)
            for l in range(len(self.prog)):
                if len(self.prog[l]) < longest:
                    for i in range(longest - len(self.prog[l])):
                        self.prog[l] += " "
        except IOError:
            self.errprint("can't open file '" + filename + "'")
            sys.exit(1)
        self.reset()
    
    def dir2string(self, d):
        """Change a direction id to a string."""
        if d == self.PATH_DIRECTION_RIGHT:
            return "right"
        elif d == self.PATH_DIRECTION_DOWN:
            return "down"
        elif d == self.PATH_DIRECTION_LEFT:
            return "left"
        elif d == self.PATH_DIRECTION_UP:
            return "up"
    
    def debug(self, msg):
        """Print a debug message."""
        if self.verbose == True:
            self.errprint("(" + str(self.x) + "," + str(self.y) + ") " + msg)
    
    def runplugins(self):
        for plugin in self.plugins:
            if plugin.call(self) == False:
                return False
    
    def step(self):
        """Step through a single symbol of the program. Return false if end of program encountered."""
        cursym = self.prog[self.y][self.x]

        if self.s == True:
            self.s = False
        elif self.runplugins() == False:
            cursym
        elif cursym == '$':
            self.debug("Start")
        elif cursym == '#':
            self.debug("End")
            return 1
        elif cursym == '!':
            self.s = True
            self.debug("Skip next symbol")
        elif cursym == '}':
            self.p += 1
            if self.p > len(self.mem) - 1:
                self.mem.append(0)
            self.debug("New memory cell: " + str(self.p))
        elif cursym == '{':
            if self.p > 0:
                self.p -= 1
            self.debug("New memory cell: " + str(self.p))
        elif cursym == '/':
            if self.d == self.PATH_DIRECTION_RIGHT:
                self.d = self.PATH_DIRECTION_UP
            elif self.d == self.PATH_DIRECTION_DOWN:
                self.d = self.PATH_DIRECTION_LEFT
            elif self.d == self.PATH_DIRECTION_LEFT:
                self.d = self.PATH_DIRECTION_DOWN
            elif self.d == self.PATH_DIRECTION_UP:
                self.d = self.PATH_DIRECTION_RIGHT
            self.debug("New direction: " + self.dir2string(self.d))
        elif cursym == '\\':
            if self.d == self.PATH_DIRECTION_RIGHT:
                self.d = self.PATH_DIRECTION_DOWN
            elif self.d == self.PATH_DIRECTION_DOWN:
                self.d = self.PATH_DIRECTION_RIGHT
            elif self.d == self.PATH_DIRECTION_LEFT:
                self.d = self.PATH_DIRECTION_UP
            elif self.d == self.PATH_DIRECTION_UP:
                self.d = self.PATH_DIRECTION_LEFT
            self.debug("New direction: " + self.dir2string(self.d))
        elif cursym == '>':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_RIGHT
                self.debug("New direction: " + self.dir2string(self.d))
        elif cursym == 'v':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_DOWN
                self.debug("New direction: " + self.dir2string(self.d))
        elif cursym == '<':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_LEFT
                self.debug("New direction: " + self.dir2string(self.d))
        elif cursym == '^':
            if self.mem[self.p] != 0:
                self.d = self.PATH_DIRECTION_UP
                self.debug("New direction: " + self.dir2string(self.d))
        elif cursym == '+':
            self.mem[self.p] += 1
            if (self.mem[self.p] == 256):
                self.mem[self.p] = 0
            self.debug("Incremented memory cell " + str(self.p) + " to " + str(self.mem[self.p]))
        elif cursym == '-':
            self.mem[self.p] -= 1
            if (self.mem[self.p] == -1):
                self.mem[self.p] = 255
            self.debug("Decremented memory cell " + str(self.p) + " to " + str(self.mem[self.p]))
        elif cursym == ',':
            self.mem[self.p] = ord(sys.stdin.read(1))
            self.debug("Inputted " + str(self.mem[self.p]) + " to memory cell " + str(self.p))
        elif cursym == '.':
            sys.stdout.write(chr(self.mem[self.p]))
            self.debug("Outputted " + str(self.mem[self.p]) + " from memory cell " + str(self.p))

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
            return 1

        return 0
    
    def run(self):
        """Run the entire program."""
        while self.step() == 0:
            1

    def __add__(self, x):
        """Step thru x symbols. Return false if end of program encountered."""
        ret = 0
        for i in range(x):
            ret = self.step()
            if ret == false:
                return ret
        return ret
