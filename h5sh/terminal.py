import shutil

class Terminal:
    """
    Fallback terminal manager.
    Does not support autocompletion and navigating the history.
    Suppresses colours in output.
    """

    class History:
        """
        Manages the history of entered commands.
        The list can be accessed through History.history.
        """

        def __init__(self, maxLength=500):
            self._history = []
            self._maxLength = maxLength
            self._histPtr = 0
            self._current = ""

        def __nonzero__(self):
            """True if the history is non-empty."""
            
            return not self._history

        def back(self, current):
            """
            Move back one element in the history.
            Raises an IndexError if already at the beginning of the history.

            :param current: String currently visible in terminal.
                            Is ignored if not at end of history.

            :returns:
                Item in the history after moving back one step.
            """

            if self._histPtr == 0:
                raise IndexError("Tried to go beyond start of history.")
            if self._histPtr == len(self._history):
                self._current = current
            self._histPtr -= 1
            return self._history[self._histPtr]

        def forward(self):
            """
            Move forward by one element in the history.
            Raises an IndexError if already at the end of the history.

            :returns:
                Item in the history after moving forward one step.
            """

            if self._histPtr == len(self._history):
                raise IndexError("Tries to got beyond end of history.")

            self._histPtr += 1
            if self._histPtr == len(self._history):
                return self._current
            return self._history[self._histPtr]

        def append(self, item):
            """Append a new item to the history and move the history pointer to the end."""

            if not self._history or item != self._history[-1]:
                self._history.append(item)
                self._histPtr = len(self._history)
            # overflow length => crop list
            if len(self._history) > self._maxLength:
                self._history = self._history[1:]
                self._histPtr -= 1

        def reset(self):
            """Reset all changes done by History.back() and History.forward()."""
            
            self._current = ""
            self._histPtr = len(self._history)

        def dump(self, showNumbers=True):
            """Return a string representation of the history."""
            
            if showNumbers:
                return "\r\n".join("{:5d}  {:s}".format(i, self._history[i])
                                   for i in range(len(self._history)))

            return "\r\n ".join("{:s}".format(item)
                                for item in self._history)


    class Colour:
        """Colours for output. Numbers correspond to ANSI escape codes."""

        black  = 30
        red    = 31
        green  = 32
        yellow = 33
        blue   = 34
        purple = 35
        cyan   = 36
        white  = 37

        iblack  = 90
        ired    = 91
        igreen  = 92
        iyellow = 93
        iblue   = 94
        ipurple = 95
        icyan   = 96
        iwhite  = 97


    def __init__(self):
        self.history = self.History()

    def get_input(self, prompt):
        """
        Query user for input.

        :returns:
            The string entered. If the user entered EOF, 'exit' is returned.
        """

        inp = None
        while not inp:
            try:
                inp = input(prompt)
            except EOFError:  # entered EOF (ctrl+d)
                self.print("exit")
                inp = "exit"
            except KeyboardInterrupt:  # pressed ctrl+c
                self.print()
        self.history.append(inp)
        return inp

    def print(self, *args, **kwargs):
        """Print something to the terminal."""

        print(*args, **kwargs)

    def get_width(self):
        """Return current the number of columns of the terminal."""

        return shutil.get_terminal_size().columns

    def coloured(self, string, colour):
        """Fallback: returns string without change."""

        return string
