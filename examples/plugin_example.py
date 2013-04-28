# PATH plugin example

# A PATH plugin allows the user to extend the PATH interpreter to
# add new features to the language. They are written in Python.
# The plugins must have the extension .py and be located in one
# of the following directories:
#
# /usr/lib/path/
# ~/.path/

# This example code adds a new symbol, "?", to the interpreter, that
# displays how many times the symbol has been used. It is a good
# example of how to create new symbols.

# Directions. These numbers are the different possible values of
# pathobj.d.
PATH_DIRECTION_RIGHT = 1
PATH_DIRECTION_DOWN = 2
PATH_DIRECTION_LEFT = 3
PATH_DIRECTION_UP = 4

# Class for the plugin.
class exampleplugin:
    """Plugin description"""
    def __init__(self):
        # Initialize stuff for your plugin here.
        self.count = 0 # A counter for how many times

    # The call function is called by the interpreter for every symbol.
    def call(self, pathobj):
        # The interpreter state is in pathobj.
        # The following variables are particularly important:
        #
        # pathobj.prog: 2-dimensional array of characters that make up the program
        # pathobj.x: current x position
        # pathobj.y: current y position
        # pathobj.mem: array of memory cells
        # pathobj.p: current memory cell pointer
        # pathobj.d: current direction (see PATH_DIRECTION_* above)
        # pathobj.s: whether the next cell is being skipped

        # The following is the easiest way to check what the current symbol is.
        if pathobj.prog[pathobj.y][pathobj.x] == '?':

            # You should use pathobj.debug() to output debug messages.
            # The messages will only display if the user has --debug enabled.
            pathobj.debug("? operator used")

            # Print out how many times this has been used
            self.count += 1
            print(self.count)

            # If you return False, the interpreter will stop processing the
            # current symbol and move on to the next one. Good for redefining
            # the built-in symbols.
            return False
        else:
            # If you return True, the interpreter will continue processing
            # the current symbol.
            return True

# This line adds the plugin to the interpreter.
glob_path.addplugin(exampleplugin())
