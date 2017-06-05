class Terminal:
    
    class History:
        def __init__(self, maxLength=500):
            self._history = []
            self._maxLength = maxLength
            self._histPtr = 0
            self._current = ""

        def __nonzero__(self):
            return len(self.history) != 0

        # current ignored when not at end of history
        def back(self, current):
            if self._histPtr == 0:
                raise IndexError("Tried to go beyond start of history.")
            if self._histPtr == len(self._history):
                self.current = current
            self._histPtr -= 1
            return self._history[self._histPtr]

        def forward(self):
            if self._histPtr == len(self._history):
                raise IndexError("Tries to got beyond end of history.")
            
            self._histPtr += 1
            if self._histPtr == len(self._history):
                return self._current
            else:
                return self._history[self._histPtr]

        # sets ptr to end
        def append(self, item):
            if len(self._history) == 0 or item != self._history[-1]:
                self._history.append(item)
                self._histPtr = len(self._history)
            if len(self._history) > self._maxLength:
                self._history = self._history[1:]
                self._histPtr -= 1
            
        def reset(self):
            self._current = ""
            self._histPtr = len(self._history)


        def dump(self, showNumbers=True):
            if showNumbers:
                return "\r\n".join("{:5d}  {:s}".format(i, self._history[i])
                               for i in range(len(self._history)))
            else:
                return "\r\n ".join("{:s}".format(item)
                               for item in self._history)

            
    def __init__(self):
        self.history = self.History()
        self.prompt = "$ "

    def activate(self):
        class TermMngr:
            def __enter__(self):
                pass

            def __exit__(self, exc_type, exc_value, traceback):
                return False
            
        return TermMngr()
    
    def get_input(self):
        inp = None
        while not inp:
            try:
                inp = input(self.prompt)
            except EOFError:
                self.print("exit", end="")
                inp = "exit"
            except KeyboardInterrupt:
                self.print()
        self.history.append(inp)
        return inp

    def print(self, *args, **kwargs):
        print(*args, **kwargs)
    
