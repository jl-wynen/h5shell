import sys
import termios
import tty

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

        # mapps special input character codes to functions that do soemthing appropriately
        self._do = {
            ASCII.ETX: self._do_abort,
            ASCII.EOT: self._do_exit,
            ASCII.BS:  self._do_delete_backwards,
            ASCII.TAB: self._do_autocomplete,
            ASCII.LF:  self._do_enter,
            ASCII.VT:  self._do_enter,
            ASCII.FF:  self._do_enter,
            ASCII.CR:  self._do_enter,
            ASCII.ESC: self._do_escape_sequence,
            ASCII.DEL: self._do_delete_backwards
        }
        # ignore all other ASCII control codes
        for key in [0,1,2,5,6,7]+list(range(14,27))+list(range(28,32)):
            self._do[key] = self._do_ignore

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
                # TODO why doesnt this work?
                # self.print(chr(ASCII.ESC)+"[{}D".format(amt), end="")
                self.print((chr(ASCII.ESC)+"[D")*-amt, end="")

    def _move_cursor_right(self, amt=1):
        """Shift cursor right by amt."""
        if amt == 0:
            pass
        elif self._cursor <= len(self._inStr)-amt:
            self._cursor += amt
            if amt == 1:
                self.print(chr(ASCII.ESC)+"[C", end="")
            else:
                # TODO
                # self.print(chr(ASCII.ESC)+"[{}D".format(amt), end="")
                self.print((chr(ASCII.ESC)+"[D")*amt, end="")

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
            self._inStr = left+right

            # move cursor left one, remove everything after it, and print right
            # this moves cursor to end of line
            self.print(chr(ASCII.ESC)+"[D"+chr(ASCII.ESC)+"[K"+right, end="")
            self._cursor += len(right)-1
            # move cursor back
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
        """Insert a string into the input; adjust cursor"""
        self._inStr += s
        self._cursor += len(s)
        self.print(s, end="")
    
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

    def activate(self):
        """
        Prime the terminal for input.
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
        self.print(self.prompt, end="")
        self._inStr = ""
        self._cursor = 0
        while True:
            inp = self._handle_input(sys.stdin.read(1))
            if inp:
                return inp


    def print(self, *args, end="\n", **kwargs):
        """
        Print something to the terminal.
        The built in print function does not work properly when in raw mode.
        """
        if self._rawMode:
            if end:
                # need explicit carriage return
                print(*args, end=end+"\r", **kwargs)
            else:
                print(*args, end="", **kwargs)
        else:
            print(*args, end=end, **kwargs)
            
        sys.stdout.flush()
        
