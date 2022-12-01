import re
import bezier

class PathParser:
    def __init__(self, string):
        self.init = None
        self.prev = None
        self.last = complex(0, 0)
        self.commands = []

        string = re.sub(r' (?=[mlhvcsqtazMLHVCSQTAZ])', '#', string)
        for command, args in [(token[0], [float(val) for val in token[2:].split() if val != '']) for token in string.split('#')]:
            length = 0
            if command in 'mlML': length = 2
            if command in 'hvHV': length = 1
            if command in 'cC': length = 6
            if command in 'sS': length = 4
            if command in 'qQ': length = 4
            if command in 'tT': length = 2

            if command in 'zZ':
                self.commands.append((command, []))
            elif command in 'mM':
                self.commands.append((command, args[:length]))
                for i in range(length, len(args), length):
                    self.commands.append(('l' if command == 'm' else 'L', args[i:i + length]))
            else:
                for i in range(0, len(args), length):
                    self.commands.append((command, args[i:i + length]))

    def next_points(self):
        if not self.commands: return False, None
        command, args = self.commands[0]
        self.commands = self.commands[1:]
        new_shape = False
        if command in 'mM':
            self.init = None
        elif self.init is None:
            new_shape = True
            self.init = self.last

        if command not in 'hvHV':
            args = [complex(x, y) for x, y in zip(args[0::2], args[1::2])]
            if command.islower():
                args = [self.last + arg for arg in args]
        if command == 'h': args = [self.last + complex(args[0], 0)]
        if command == 'v': args = [self.last + complex(0, args[0])]
        if command == 'H': args = [complex(args[0], self.last.imag)]
        if command == 'V': args = [complex(self.last.real, args[0])]

        if command in 'mM':
            self.last = args[0]
            return new_shape, []
        if command in 'zZ':
            last = self.last
            self.last = self.init
            return new_shape, [last, self.init]
        if command in 'lhvLHV':
            last = self.last
            self.last = args[0]
            return new_shape, [last] + args
        if command in 'cC':
            points = bezier.cubic_bezier(self.last, *args)
            self.prev = args[-2]
            self.last = args[-1]
            return new_shape, points
        if command in 'sS':
            points = bezier.smooth_cubic_bezier(self.prev, self.last, *args)
            self.prev = args[-2]
            self.last = args[-1]
            return new_shape, points
        if command in 'qQ':
            points = bezier.quadratic_bezier(self.last, *args)
            self.prev = args[-2]
            self.last = args[-1]
            return new_shape, points
        if command in 'tT':
            points = bezier.smooth_quadratic_bezier(self.prev, self.last, *args)
            self.prev = self.last
            self.last = args[-1]
            return new_shape, points
