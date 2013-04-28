# File I/O plugin for PATH
# This plugin lets you redirect input and output to a file.
# (c) 2004 Francis Rogers. License is the same as that for the PATH interpreter.

class FileIO:
    """Plugin that redirects input and output to a file."""
    def __init__(self):
        self.file_active = False
        self.file_broke = False
        self.openfile = None
        self.old_in = None
        self.old_out = None

    def call(self, pathobj):
        cursym = pathobj.prog[pathobj.y][pathobj.x]

        if cursym == '&':
            filename = ""
            i = pathobj.p
            while pathobj.mem[i] != 0:
                filename += chr(pathobj.mem[i])
                i += 1
                if i > len(pathobj.mem) - 1:
                    pathobj.mem.append(0)
            pathobj.debug("Opening file " + filename)

            if filename == "":
                pathobj.redefine_io(self.old_in, self.old_out)
                self.file_broke = False
                self.file_active = False
                return False
            try:
                self.openfile = open(filename, "a+")
            except IOError:
                self.file_broke = True
            if pathobj.func_in != self.filein:
                self.old_in = pathobj.func_in
            if pathobj.func_out != self.fileout:
                self.old_out = pathobj.func_out
            pathobj.redefine_io(self.filein, self.fileout)
            self.file_active = True
            return False
        else:
            return True

    def filein(self):
        try:
            if self.file_broke == True:
                raise IOError
            return self.openfile.read(1)
        except IOError:
            return 0

    def fileout(self, char):
        try:
            if self.file_broke == True:
                raise IOError
            return self.openfile.write(char)
        except IOError:
            return 0

glob_path.addplugin(FileIO())
