# PyPATH: Python expressions plugin for PATH
# This plugin offers inline execution of Python expressions and statements in a PATH program.
# (c) 2004 Francis Rogers. License is the same as that for the PATH interpreter.

class pypath:
    """Plugin that allows inline execution of Python expressions and statements."""
    def __init__(self):
        self.py_eval_active = False
        self.py_exec_active = False
        self.py_buffer = ""

    def call(self, pathobj):
        cursym = pathobj.prog[pathobj.y][pathobj.x]
        if self.py_eval_active == True:
            if cursym == '@':
                result = eval(self.py_buffer, {'pathobj' : pathobj})
                if type(result) is int:
                    pathobj.debug("Storing result " + str(result) + " to memory cell " + pathobj.p)
                    pathobj.mem[pathobj.p] = result
                elif type(result) is float:
                    pathobj.debug("Storing result " + str(result) + " to memory cell " + pathobj.p)
                    pathobj.mem[pathobj.p] = result.round()
                elif type(result) is str:
                    i = pathobj.p
                    for c in result:
                        pathobj.debug("Storing character " + str(ord(c)) + " to memory cell " + str(i))
                        if i > len(pathobj.mem) - 1:
                            pathobj.mem.append(0)
                        pathobj.mem[i] = ord(c)
                        i += 1
                self.py_eval_active = False
                self.py_buffer = ""
                return False
            else:
                self.py_buffer += cursym
                return False
        elif self.py_exec_active == True:
            if cursym == '%':
                exec(self.py_buffer, {'pathobj' : pathobj})
                pathobj.debug("Python statement executed")
                self.py_exec_active == False
                self.py_buffer = ""
                return False
            else:
                self.py_buffer += cursym
                return False
	elif cursym == '@':
		pathobj.debug("Started Python expression")
		self.py_eval_active = True
		return False
	elif cursym == '%':
		pathobj.debug("Started Python statement")
		self.py_exec_active = True
		return False
	else:
		return True

glob_path.addplugin(pypath())
