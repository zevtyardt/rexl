import argparse
import functools
import copy

from typing import Optional, Callable, Union
from cmd2 import constants
from cmd2.parsing import Statement
from cmd2.decorators import _set_parser_prog
from cmd2.exceptions import Cmd2ArgparseError

def validate_facebook_access_token(func: Callable) -> Callable:
    @functools.wraps(func)
    def func_wrap(self, param):
        if not self.facebook_user_access_token or self.facebook_user_access_token == "None":
            self.perror("Set access token first!")
            return
        return func(self, param)
    return func_wrap

def use_for(modules: Union[list, tuple, set]) -> Callable:
    from .constants import USE_FOR
    if not isinstance(modules, (list, tuple, set)):
        modules = [(modules,)]
    def wrap(func: Callable) -> Callable:
        setattr(func, USE_FOR, modules)
        return func
    return wrap

def with_argparser(parser: argparse.ArgumentParser, *,
                   ns_provider: Optional[Callable[..., argparse.Namespace]] = None,
                   preserve_quotes: bool = False) -> Callable[[argparse.Namespace], Optional[bool]]:
    """A decorator to alter a cmd2 method to populate its ``args`` argument by parsing arguments
    with the given instance of argparse.ArgumentParser.

    :param parser: unique instance of ArgumentParser
    :param ns_provider: An optional function that accepts a cmd2.Cmd object as an argument and returns an
                        argparse.Namespace. This is useful if the Namespace needs to be prepopulated with
                        state data that affects parsing.
    :param preserve_quotes: if True, then arguments passed to argparse maintain their quotes
    :return: function that gets passed the argparse-parsed args in a Namespace
             A member called __statement__ is added to the Namespace to provide command functions access to the
             Statement object. This can be useful if the command function needs to know the command line.

    :Example:

    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('-p', '--piglatin', action='store_true', help='atinLay')
    >>> parser.add_argument('-s', '--shout', action='store_true', help='N00B EMULATION MODE')
    >>> parser.add_argument('-r', '--repeat', type=int, help='output [n] times')
    >>> parser.add_argument('words', nargs='+', help='words to print')
    >>>
    >>> class MyApp(cmd2.Cmd):
    >>>     @cmd2.with_argparser(parser, preserve_quotes=True)
    >>>     def do_argprint(self, args):
    >>>         "Print the options and argument list this options command was called with."
    >>>         self.poutput('args: {!r}'.format(args))
    """
    import functools

    parser = copy.deepcopy(parser)
    def arg_decorator(func: Callable):
        @functools.wraps(func)
        def cmd_wrapper(cmd2_app, statement: Union[Statement, str]):
            statement, parsed_arglist = cmd2_app.statement_parser.get_command_arg_list(command_name, statement, preserve_quotes)

            if ns_provider is None:
                namespace = None
            else:
                namespace = ns_provider(cmd2_app)

            try:
                args = parser.parse_args(parsed_arglist, namespace)
            except SystemExit:
                raise Cmd2ArgparseError
            else:
                setattr(args, '__statement__', statement)
                if parser.usage:
                    setattr(args, 'print_usage', "usage: " + parser.usage)
                return func(cmd2_app, args)

        # argparser defaults the program name to sys.argv[0], but we want it to be the name of our command
        command_name = func.__name__[len(constants.COMMAND_FUNC_PREFIX):]
        command_name = command_name.split("__")[0].replace("_", "-")
        _set_parser_prog(parser, command_name)

        if func.__doc__:
            parser.description = func.__doc__

        # set formatter class
        parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(
            prog, max_help_position=50)

        # Set the command's help text as argparser.description (which can be None)
        cmd_wrapper.__doc__ = parser.description

        # Set some custom attributes for this command
        setattr(cmd_wrapper, constants.CMD_ATTR_ARGPARSER, parser)
        setattr(cmd_wrapper, constants.CMD_ATTR_PRESERVE_QUOTES, preserve_quotes)

        return cmd_wrapper

    # noinspection PyTypeChecker
    return arg_decorator

