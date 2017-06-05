import argparse

class Command:
    
    class ArgumentError(RuntimeError):
        def __init__(self, message):
            self.message = message

    class ExitParser(Exception):
        pass

    
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            raise Command.ArgumentError(message)

        def exit(self, status=0, message=None):
            raise Command.ExitParser()

    def __init__(self, term):
        self._term = term
        self._parser = None

    def _parse_args(self, args):
        if self._parser:
            try:
                return self._parser.parse_args(args)
            except self.ArgumentError as e:
                self._term.print("{usage}{message}".format(usage=self._parser.format_usage(),
                                                           message=e.message))
                return None
            except self.ExitParser:
                return None
