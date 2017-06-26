import sys
import os
import termios
import tty

try:
    import psutil
    have_psutil = True
except ImportError:
    have_psutil = False

from ascii_codes import ASCII
from terminal import Terminal

class VT100(Terminal):
    """
    Manager for VT100 emulators.
    Supports more advanced features than the fallback but must be activated bafore use.
    """
    
    def __init__(self):
        super(VT100, self).__init__()

        self.inFD = sys.stdin.fileno()
        self._rawMode = False
        self._inStr = ""
        self._cursor = 0 # relative to inStr, not counting prompt
        
        # function to handle a single character of input
        self._handle_input = self._default_input_handle

        # maps special input character codes to functions that do soemthing appropriately
        self._do = {}

        # ignore all ASCII control codes by default
        for key in range(32):
            self._do[key] = self._do_ignore

        # set used control codes
        self._do[ASCII.ETX] = self._do_abort
        self._do[ASCII.EOT] = self._do_exit
        self._do[ASCII.BS]  = self._do_delete_backwards
        self._do[ASCII.TAB] = self._do_autocomplete
        self._do[ASCII.LF]  = self._do_enter
        self._do[ASCII.VT]  = self._do_enter
        self._do[ASCII.FF]  = self._do_enter
        self._do[ASCII.CR]  = self._do_enter
        self._do[ASCII.ESC] = self._do_escape_sequence
        self._do[ASCII.DEL] = self._do_delete_backwards
        if have_psutil:
            self._do[ASCII.SUB] = self._do_suspend
            
        # maps escape sequences to some functions
        self._do_esc = {
            "[A": self._do_up,
            "[B": self._do_down,
            "[C": self._do_right,
            "[D": self._do_left
        }

    def _raw_mode(self):
        """
        Switch terminal to raw mode.
        Attention:
        Must be switched back before the program terminates!
        See VT100._reset() and VT100.activate().
        """
        
        self._oldattrs = termios.tcgetattr(self.inFD)
        try:
            tty.setraw(self.inFD)
            self._rawMode = True
        except:
            self.print("Unable to switch terminal to raw mode.")
            termios.tcsetattr(self.inFD, termios.TCSADRAIN, self._oldattrs)
            raise
        
    def _reset(self):
        """Reset the terminal to its previous state before calling VT100._raw_mode()."""
        termios.tcsetattr(self.inFD, termios.TCSADRAIN, self._oldattrs)
        self._rawMode = False
    
    def _move_cursor_left(self, amt=1):
        """Shift cursor left by amt."""
        if amt == 0:
            pass
        elif self._cursor >= amt:
            self._cursor -= amt
            if amt == 1:
                self.print(chr(ASCII.ESC)+"[D", end="")
            else:
                self.print(chr(ASCII.ESC)+"[{}D".format(amt), end="")

    def _move_cursor_right(self, amt=1):
        """Shift cursor right by amt."""
        if amt == 0:
            pass
        elif self._cursor <= len(self._inStr)-amt:
            self._cursor += amt
            if amt == 1:
                self.print(chr(ASCII.ESC)+"[C", end="")
            else:
                self.print(chr(ASCII.ESC)+"[{}D".format(amt), end="")

    def _clear_output_from_cursor(self):
        """Erase all printed output to the right of cursor. Does not change _inStr"""
        self.print(chr(ASCII.ESC)+"[K", end="")

    def _clear_input(self):
        """Erase all input both in _inStr and in the terminal."""
        if self._inStr:
            self._inStr = ""
            if self._cursor > 0:
                self._move_cursor_left(self._cursor)
            self._clear_output_from_cursor()
                
    def _do_up(self):
        """Handle 'cursor up' command. Navigates history."""
        try:
            aux = self.history.back(self._inStr)
        except IndexError:
            return
        self._clear_input()
        if aux:
            self._insert(aux)

    def _do_down(self):
        """Handle 'cursor down' command. Navigates history."""
        try:
            aux = self.history.forward()
        except IndexError:
            return
        self._clear_input()
        if aux:
            self._insert(aux)

    def _do_right(self):
        """Handle 'cursor right' command. Simply shifts cursor."""
        self._move_cursor_right()

    def _do_left(self):
        """Handle 'cursor left' command. Simply shifts cursor."""
        self._move_cursor_left()

    def _do_suspend(self):
        """
        Suspend the shell process.
        Only works if psutil module is available.
        """

        # cleanly hand over the terminal
        if self._rawMode:
            self._reset()
            backToRaw = True
        else:
            backToRaw = False
        currentCursor = self._cursor

        # suspend the current process (requires psutil)
        p = psutil.Process()
        p.suspend()

        # re-initialize terminal
        if backToRaw:
            self._raw_mode()
        self.print(self.prompt+self._inStr, end="")
        self._cursor = len(self._inStr)
        self._move_cursor_left(len(self._inStr)-currentCursor)
        
    def _do_abort(self):
        """Abort and clear current input; reprint prompt."""
        self.print("^C")
        self._inStr = ""
        self._cursor = 0
        self.history.reset()
        self.print(self.prompt, end="")

    def _do_exit(self):
        """Returns 'exit' if input is empty."""
        if not self._inStr:
            self.print("exit")
            return "exit"
            
    def _do_delete_backwards(self):
        """Remove one character before the cursor."""
        if self._cursor > 0:
            left = self._inStr[:self._cursor-1]
            right = self._inStr[self._cursor:]
            self._inStr = left

            self._move_cursor_left()
            self._clear_output_from_cursor()
            self._insert(right)
            self._move_cursor_left(len(right))

    def _do_autocomplete(self):
        """TODO: implement"""
        pass

    def _do_enter(self):
        """
        Enter the input into history and return it.
        Only reprints prompt if input is empty.
        """
        if self._inStr:
            self.history.append(self._inStr)
            self.print()
            return self._inStr
        else:
            self.print()
            self.print(self.prompt, end="")

    def _do_escape_sequence(self):
        """Switch state to inputting escape sequence."""
        self._handle_input = self._esc_input_handle
        self._escSeq = ""

    def _do_ignore(self):
        """Don't do nothing."""
        pass

    def _insert(self, s):
        """Insert a string into the input at cursor; adjust cursor"""

        # modify internal string
        left = self._inStr[:self._cursor]
        right = self._inStr[self._cursor:]
        self._inStr = left+s+right

        # display
        # don't clear, just overwrite
        self.print(s+right, end="")
        self._cursor = len(self._inStr)
        self._move_cursor_left(len(right))
    
    def _default_input_handle(self, c):
        """
        Handle input of single characters via VT100._do.
        Returns:
        Result of function associated with c.
        """
        try:
            return self._do[ord(c)]()
        except KeyError:
            self._insert(c)
            # no return -> definately not done yet
        
    def _esc_input_handle(self, c):
        """
        Handle input of escape sequences.
        Collects characters for sequence and execute it once complete.
        Switches back to _default_input_handle when done.
        Returns:
        Result of executing function for escape sequence.
        """
        self._escSeq += c
        oc = ord(c)

        if c != "[" and oc >= 64 and oc <= 126:
            self._handle_input = self._default_input_handle
            try:
                return self._do_esc[self._escSeq]()
            except KeyError:
                self._insert("^"+self._escSeq)

    def _activate(self):
        """
        Switches to raw mode and returns a context manager to switch back
        when the shell is terminated.
        """
        class TermMngr:
            def __init__(self, term):
                self.term = term
            def __enter__(self):
                pass
            def __exit__(self, exc_type, exc_value, traceback):
                self.term._reset()
                return False
        
        self._raw_mode()
        return TermMngr(self)
            
    def get_input(self):
        """
        Query user for input.
        Return:
        The string entered. If the user entered EOF, 'exit' is returned.
        """
        with self._activate():
            self.print(self.prompt, end="")
            self._inStr = ""
            self._cursor = 0
            inp = None
            while not inp:
                inp = self._handle_input(sys.stdin.read(1))
        return inp

    def print(self, *args, end="\n", **kwargs):
        """
        Print something to the terminal.
        The built in print function does not work properly when in raw mode.
        """
        if self._rawMode:
            outp = [s.replace("\n", "\n\r") if isinstance(s,str) else s for s in args]
            if end:
                # need explicit carriage return
                print(*outp, end=end+"\r", **kwargs)
            else:
                print(*args, end="", **kwargs)
        else:
            print(*args, end=end, **kwargs)
            
        sys.stdout.flush()

    def get_width(self):
        nrows, ncols = os.popen("stty size", "r").read().split()
        return int(ncols)

    def coloured(self, string, colour):
        return chr(ASCII.ESC)+"["+str(colour)+"m"+string+chr(ASCII.ESC)+"[0m"
