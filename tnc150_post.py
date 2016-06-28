import datetime
from abc import ABCMeta
from abc import abstractmethod
import FreeCAD
now = datetime.datetime.now()
FMAX = 6000

# to distinguish python built-in open function from the one declared below
if open.__module__ == '__builtin__':
    pythonopen = open

class AbstractOperation:
    __metaclass__ = ABCMeta
    @abstractmethod
    def compile(self):
        pass

    @abstractmethod
    def fromParameters(self, p):
        pass

class LinearInterpolation(AbstractOperation):
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.f = 0
        self.m = None

    def compile(self):
        if not self.x and not self.y and not self.z:
            return "L    R F M"

        ret = "L "
        if self.x:
            ret += "X%+5.3f " %self.x
        if self.y:
            ret += "Y%+5.3f " %self.y
        if self.z:
            ret += "Z%+5.3f " %self.z

        ret += "R F"

        if self.f:
            ret += str(self.f)

        ret += " M"

        if self.m:
            ret += " %d" %self.m

        return ret

    def fromParameters(self, p):
        for k in p.keys():
            if k == 'X':
                self.x = float(p[k])
            elif k == 'Y':
                self.y = float(p[k])
            elif k == 'Z':
                self.z = float(p[k])
            elif k == 'F':
                self.f = int(p[k])
            elif k == 'M':
                self.m = int(p[k])
            else:
                print "Invalid parameter: " + k + '\n'

def export(objectslist,filename):
    blocks = ["BEGIN_PGM 1 MM"]

    for obj in objectslist:
        if hasattr(obj, "Path"):
            blocks += parse(obj.Path)

    row = 0
    code = ""
    for b in blocks:
        code += str(row) + ' ' + b + '\n'
        row += 1

    code += str(row) + ' ' + "STOP M2" + '\n'
    code += str(row) + ' ' + "END_PGM 1 MM" + '\n'

    outfile = pythonopen(filename,"wb")
    outfile.write(code)
    outfile.close()

def parse(path):
    output = []
    i = 0
    for c in path.Commands:
        if c.Name in {'G00', 'G01'}:
            op = LinearInterpolation()
            op.fromParameters(c.Parameters)
            if c.Name == 'G00':
                op.f = FMAX
            output.append(op.compile())
        else:
            output.append("Invalid name: " + c.Name)

    return output

print __name__ + " postprocessor loaded."

