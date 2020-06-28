import cmd2
import re
import random
import textwrap
import tabulate
import shutil
import inquirer
import os
import argparse

from lib.decorators import with_argparser
from cmd2 import style, fg
from cmd2.utils import alphabetical_sort, Settable
from cmd2.parsing import Statement
from argparse import Namespace as ns
from typing import Union, Optional
from colorama.ansi import clear_screen

try:
    from . import constants
except ImportError:
    class constants:
        APP_NAME = "default"
        APP_VERSION = "0.0.0"
        AUTHOR_USERNAME = "zevtyardt"

class CustomCmd(cmd2.Cmd):
    def __init__(self, msf_style: bool = False, prompt_suffix: str = ">"):
        super().__init__()
        self.default_error = "{!r} is not a recognized command!"
        self.style = style
        self.fg = fg

        self.prompt_suffix = prompt_suffix
        self.msf_style = msf_style
        self.module_delimeter = "." if not msf_style else "/"

        self.__version__ = constants.APP_VERSION
        self.__author__ = constants.AUTHOR_USERNAME

        self.register_preloop_hook(self._preloop_hook)
        self.register_precmd_hook(self._commands_completion_hook)

        self._appname = constants.APP_NAME
        self.prompt = self._appname

        self.current_module = self._appname

        del cmd2.Cmd.do_py
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do__relative_run_script

        self.hidden_commands.extend([
            'alias', 'edit', 'macro', 'shell', 'shortcuts', "history"
        ])

        self.modules = {}
        self.total = argparse.Namespace(commands=0, modules=0, submodules=set(), auxilaries=set())
        self.g_commands = []
        self._alias_commands = {}
        self._revalias_commands = {}

        self._category_pattern = re.compile(
            r"^(?P<command>.+?)__(?P<category>.+?)(?:__(?P<subcategory>.+?))?$")
        self._max_lenght = 0
        self.register_custom_commands()
        self.reset_module()

        self._cmdfmt = self._custom_help_format()
        self._command = None

    @property
    def get_terminal_size(self) -> os.terminal_size:
        """get the size of terminal window"""
        return shutil.get_terminal_size()

    def register_custom_commands(self) -> None:
        def update_max_lenght(lenght: Union[int, str]) -> None:
            if isinstance(lenght, str):
                lenght = len(lenght)
            if lenght > self._max_lenght:
                self._max_lenght = lenght
        tp_commands = []
        for raw in self.get_visible_commands():
            recmd = self._category_pattern.search(raw)
            cmd_func = self.cmd_func(raw)
            if recmd is not None:
                data = ns(**recmd.groupdict())
                key = data.category
                subcategory = data.subcategory
                if subcategory:
                    self.total.submodules.add(subcategory)
                    subcategory = self.module_delimeter.join(
                        subcategory.split("__"))
                    key += (self.module_delimeter + subcategory)
                if not self.modules.get(key):
                    self.modules[key] = []
                if key.lower().startswith("auxilary"):
                    self.total.auxilaries.add(raw)
                res_data = (data.command, raw)
                location_to = self.modules[key]
                if res_data not in location_to:
                    update_max_lenght(res_data[0])
                    location_to.append(res_data)
                    self.total.commands += 1
            elif not recmd and raw not in self.hidden_commands:
                alias = raw
                update_max_lenght(raw)
                if not hasattr(cmd_func, constants.USE_FOR):
                    self.g_commands.append(alias)
                self.total.commands += 1
            if hasattr(cmd_func, constants.USE_FOR):
                for module in cmd_func._USE_FOR:
                    module = self.module_delimeter.join(module)
                    if not self.modules.get(module):
                        self.modules[module] = []
                    self.modules[module].insert(
                        0, (raw if not recmd else data.command, raw))
            if hasattr(cmd_func, constants.ALIASES):
                alias = cmd_func._ALIASES
                update_max_lenght(alias)
                self._alias_commands[raw if not recmd else data.command] = alias

        self._max_lenght += 4
        self.total.modules = len(set(i.split(self.module_delimeter)[0] for i in self.modules))
        self.total.submodules = len(self.total.submodules)
        self.total.auxilaries = len(self.total.auxilaries)
        self._revalias_commands = dict([v, k] for k, v in self._alias_commands.items())

    def reset_module(self) -> None:
        for module, items in self.modules.items():
            self._disable_commands(i[1] for i in items)

    def use_module(self, modules: Union[list, str] = "") -> None:
        if isinstance(modules, str):
            modules = [modules]
        self.reset_module()
        for module in modules:
            items = self.modules.get(module)
            if items:
                self._enable_commands(i[1] for i in items)

    def _enable_commands(self, commands: Union[list, iter]) -> None:
        for command in commands:
            self.enable_command(command)

    def _disable_commands(self, commands: Union[list, iter],
                          reason: str = "You must be connected to use this command") -> None:
        for command in commands:
            self.disable_command(command, reason)

    def _add_settable(self, name, val_type, description, **kwargs) -> None:
        settable_object = Settable(
            name=name, val_type=val_type, description=description, **kwargs)
        assert not hasattr(self, name)
        setattr(self, name, None)
        self.settables[settable_object.name] = settable_object

    def get_visible_commands(self) -> list:
        def todisplay_command(raw):
            def invalid(x, force=False):
                if (real_command := self._alias_commands.get(x)):
                     return real_command
                return x.replace("_", "-") if x in self.g_commands or force else x
            cmd = self._category_pattern.search(raw)
            if self.current_module != self._appname:
                return invalid(cmd.group(1) if cmd else raw, force=True)
            return invalid(raw)
        commands = [todisplay_command(command) for command in self.get_all_commands()
                    if command not in self.hidden_commands and command not in self.disabled_commands]
        return commands

    def _convert_to_valid_command(self, command: str) -> str:
        def valid(x): return x.replace("-", "_")
        if self.current_module != self._appname:
            for v in self.modules.values():
                for (alias, real_command) in v:
                    if valid(command) == alias:
                        return real_command
        return valid(command)

    # hooks
    def _commands_completion_hook(self, data: cmd2.plugin.PrecommandData) -> cmd2.plugin.PrecommandData:
        command = data.statement.command
        # reverse
        if (real_command := self._revalias_commands.get(command)):
            command = real_command
        self._command = command
        args = " " + data.statement.args
        new_command = self._convert_to_valid_command(self._command)
        data.statement = self.statement_parser.parse(new_command + args)
        return data

    def _preloop_hook(self) -> None:
        self.set_window_title(
            f"{self._appname} framework {self.__version__} - {self.__author__}")
        self.orig_prompt = self.prompt
        self.update_prompt()

    def update_prompt(self, prefix: str = "", prompt_suffix: str = ">", sorted: bool = False, msf_style: bool = False) -> None:
        self.poutput()
        new_prompt = "%s%s" % (prefix, self.style(
            self.orig_prompt, underline=True))
        if self.current_module != self._appname:
            if sorted:
                s_module = self.current_module.split(self.module_delimeter)
                module_name = self.module_delimeter.join(
                    "_".join(s[0] for s in i.split("_"))
                    if n < len(s_module) else i
                    for n, i in enumerate(s_module, start=1))
                new_prompt += self.style(module_name, fg=self.fg.bright_green)
            if msf_style:
                s_module = self.current_module.split(self.module_delimeter, 1)
                if len(s_module) == 1:
                    s_module.insert(0, "module")
                new_prompt += f"{s_module[0]}({self.style(s_module[1], fg=self.fg.bright_red)})"
            else:
                new_prompt += " "
                new_prompt += self.style(self.current_module,
                                         fg=self.fg.bright_green)

        new_prompt += " %s " % prompt_suffix
        self.async_update_prompt(new_prompt)

    def pinfo(self, msg: str = "", **kwargs) -> None:
        prefix = self.style("[+] ", fg=self.fg.green)
        super().poutput(prefix + msg, **kwargs)

    def default(self, statement: Statement) -> Optional[bool]:
        """Executed when the command given isn't a recognized command implemented by a do_* method.

        :param statement: Statement object with parsed input
        """
        if self._command is None:
            super().default(statement)
            return 0

        if self.default_to_shell:
            if 'shell' not in self.exclude_from_history:
                self.history.append(statement)

            # noinspection PyTypeChecker
            return self.do_shell(statement.command_and_args)
        else:
            err_msg = self.default_error.format(self._command)

            # Set apply_style to False so default_error's style is not overridden
            self.perror(err_msg, apply_style=False)

    # additional commands
    def do_clear_screen(self, param) -> None:
        """clear terminal screen"""
        self.poutput(clear_screen())
        self.poutput(self.intro)

    def do_list_modules(self, params) -> None:
        """List available module"""
        if not self.modules:
            self.perror("<empty>")
        else:
            width = self.get_terminal_size.columns
            self.columnize(sorted(self.modules.keys()),
                           displaywidth=width if width < 150 else 150)

    UseParser = argparse.ArgumentParser(usage="use [-h] [-i] [module]")
    UseParser.add_argument("module", nargs="*", help="specific module to use")
    UseParser.add_argument("-i", "--interactive",
                           action="store_true", help="run interactive mode")

    @with_argparser(UseParser)
    def do_use(self, params) -> None:
        """Use a spesific module"""
        if not self.modules:
            self.perror("<empty>")
            return 0

        module_name = None
        if params.interactive:
            self.poutput()
            questions = [
                inquirer.List("module_name", message="module selected",
                              choices=sorted(self.modules.keys()))
            ]
            module_name = inquirer.prompt(questions)["module_name"]
        elif params.module:
            module_name = params.module[0]
        else:
            self.poutput(params.print_usage)

        if module_name and module_name != self.current_module:
            if self.modules.get(module_name):
                self.current_module = module_name
                self.use_module(module_name)
                self.update_prompt(prefix="\r", msf_style=self.msf_style, prompt_suffix=self.prompt_suffix)
            else:
                self.poutput("%s is not a recognized module!" % module_name)

    def complete_use(self, chars, raw, *args) -> list:
        """auto complete for 'use'"""
        raw_s = raw.strip().split()
        list_modules = [i for i in self.modules.keys() if i.startswith(chars) or chars == ""]

        if len(raw_s) > 1 and raw_s[-1] in self.modules.keys() and \
                not any(i[len(chars)] == self.module_delimeter for i in list_modules):
            return []
        return list_modules

    def do_back(self, *args) -> None:
        """Back to main module"""
        if self.current_module != self._appname:
            self.current_module = self._appname
            self.reset_module()
            self.update_prompt(prefix="\r")

    def _custom_help_format(self) -> str:
        return f"{{0:<{self._max_lenght}}}{{1}}"

    def do_help(self, *args) -> None:
        """print this help message"""
        self.poutput()
        self._print_topics((cmd, cmd) for cmd in self.g_commands)
        if self.current_module != self._appname:
            data = self.modules[self.current_module]
            self._print_topics(data, title=self.current_module)

    def _print_topics(self, data: Union[iter, list], title: str = "options",
                      indent: int = 2) -> None:
        if self.current_module == self._appname:
            prefix = ""
            self.poutput(self._cmdfmt.format("commands", "description"))
            self.poutput(self._cmdfmt.format("--------", "-----------"))
        else:
            title += ":"
            prefix = " " * indent
            self.poutput(title)
            self.poutput("-" * len(title))
        self.poutput()
        for alias, command in data:
            self.poutput(prefix + self._cmdfmt.format(
                         self._alias_commands.get(alias, alias.replace("_", "-")),
                         self.get_doc(command, prefix))
                         )
        self.poutput()

    def get_doc(self, cmd: str, prefix: str):
        def capitalize(text):
            if len(text) > 1:
                return text[0].upper() + text[1:]
            return text
        max_lenght = self.get_terminal_size.columns - self._max_lenght - 4
        cmd_func = self.cmd_func(cmd)
        doc = cmd_func.__doc__

        if not doc:
            return ""
        doc = re.sub(r"\n\s+", "\n", doc.strip())
        docs = textwrap.wrap(capitalize(doc), max_lenght)
        rawtext = [docs[0]]
        for raw in docs[1:]:
            rawtext.append(prefix + self._cmdfmt.format("", raw))
        desc = "\n".join(rawtext)
        while desc.endswith("."):
            desc = desc[:-1]
        return desc
