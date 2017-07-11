import argparse

class Command:
    class ArgumentError(RuntimeError):
        """Raised by Parser on error."""

        def __init__(self, message):
            self.message = message

    class ExitParser(Exception):
        """Raised by Parser in order to stop parsing."""
        pass

    class Parser(argparse.ArgumentParser):
        """
        Behaves like its parent but raises ArgumentError and ExitParser
        instead of printing messages directly and terminating the program.
        This allows for Parser to be used within a program and not just at the
        beginning.
        """

        def error(self, message):
            """
            Parser encountered an error.

            :raises: Command.ArgumentError
            """

            raise Command.ArgumentError(message)

        def exit(self, status=0, message=None):
            """
            Called when parser wants to exit.

            :raises: Command.ExitParser.
            """

            raise Command.ExitParser()

    def __init__(self):
        self._parser = None

    def __call__(self):
        """
        Execute the command; not allowed for base command.

        :raises: RuntimeError
        """
        raise RuntimeError("Calling base command.")

    def _parse_args(self, args, term):
        """
        Parse command line arguments with custom Parser and handle exceptions.

        :returns: Parsed arguments on success, None otherwise.
        """

        if self._parser:
            try:
                return self._parser.parse_args(args)
            except self.ArgumentError as e:
                # print the message properly
                term.print("{usage}{message}".format(usage=self._parser.format_usage(),
                                                     message=e.message))
                return None
            except self.ExitParser:
                # just keep going
                return None

    def get_description(self):
        """Returns the description of the command."""
        return self._parser.description
