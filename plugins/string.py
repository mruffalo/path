# String plugin for PATH
# This plugin adds string literals and string output to PATH programs.
# (c) 2004 Francis Rogers. License is the same as that for the PATH interpreter.

class string:
    """String literals and string output plugin."""
    def __init__(self):
        self.string_active = False
        self.string_escape = False
        self.string_buffer = ""

    def call(self, pathobj):
        cursym = pathobj.prog[pathobj.y][pathobj.x]
        if self.string_active == True:
            if self.string_escape == True:
                if cursym == '\\':
                    self.string_buffer += '\\'
                elif cursym == 'n':
                    self.string_buffer += '\n'
                elif cursym == '\"':
                    self.string_buffer += '\"'
                else:
                    self.string_buffer += '\\' + cursym
                self.string_escape = False
                return False
            elif cursym == '\"':
                self.string_buffer += chr(0)
                i = pathobj.p
                for c in self.string_buffer:
                    pathobj.debug("Storing character " + str(ord(c)) + " to memory cell " + str(i))
                    if i > len(pathobj.mem) - 1:
                        pathobj.mem.append(0)
                    pathobj.mem[i] = ord(c)
                    i += 1
                self.string_active = False
                self.string_buffer = ""
                pathobj.lock(None)
                return False
            else:
                if cursym == '\\':
                    self.string_escape = True
                else:
                    self.string_buffer += cursym
                return False
        elif cursym == '\"':
            pathobj.debug("Started string literal")
            pathobj.lock(self)
            self.string_active = True
            return False
        elif cursym == '\'':
            i = pathobj.p
            while pathobj.mem[i] != 0:
                pathobj.func_out(chr(pathobj.mem[i]))
                i += 1
                if i > len(pathobj.mem) - 1:
                    pathobj.mem.append(0)
            return False
        else:
            return True

glob_path.addplugin(string())
