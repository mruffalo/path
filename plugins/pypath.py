# PyPATH: Python expressions plugin for PATH
# This plugin offers inline execution of Python expressions and statements in a PATH program.
# (c) 2004 Francis Rogers. License is the same as that for the PATH interpreter.

class pypath:
    """Plugin that allows inline execution of Python expressions and statements."""
    def __init__(self):
        self.py_buffer = ""
        
    def call(self, pathobj):
        cursym = pathobj.prog[pathobj.y][pathobj.x]
        if cursym == '@':
            result = eval(self.getstr(pathobj), {'pathobj' : pathobj})
            if type(result) is int:
                pathobj.debug("Storing result " + str(result) + " to memory cell " + pathobj.p)
                pathobj.mem[pathobj.p] = result
            elif type(result) is float:
                pathobj.debug("Storing result " + str(result) + " to memory cell " + pathobj.p)
                pathobj.mem[pathobj.p] = result.round()
            elif type(result) is str:
                i = pathobj.p
                for c in (result + chr(0)):
                    pathobj.debug("Storing character " + str(ord(c)) + " to memory cell " + str(i))
                    if i > len(pathobj.mem) - 1:
                        pathobj.mem.append(0)
                    pathobj.mem[i] = ord(c)
                    i += 1
            return False
        elif cursym == '%':
            exec(self.getstr(pathobj), {'pathobj' : pathobj})
            pathobj.debug("Python statement executed")
            return False
        else:
            return True
        
    def getstr(self, pathobj):
        self.py_buffer = ""
        i = pathobj.p
        while pathobj.mem[i] != 0:
            self.py_buffer += chr(pathobj.mem[i])
            i += 1
            if i > len(pathobj.mem) - 1:
                pathobj.mem.append(0)
        return self.py_buffer
        

glob_path.addplugin(pypath())
