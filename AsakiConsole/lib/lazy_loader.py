from lib.constants import APP_VERSION, APP_NAME
import threading
import sys
import time

run = True
vars = []
def loading():
    import itertools

    chars = itertools.cycle([
      "....", "...", "..", ".", "..", "..."
    ])
    while run:
        if vars:
            klass = globals().get(vars[-1])
            message = f"{klass.__module__} loaded"
        else:
            message = f"Initializing"
        sys.stdout.write(
            f"\x1b[K  {message} {next(chars)}\r")
        time.sleep(0.2)
    sys.stdout.write("\x1b[K")

th = threading.Thread(target=loading)
th.daemon = True
th.start()

from lib.core import CustomCmd
import os
import re
import importlib

rilpath = sys.path[0]
for path, dirs, files in os.walk(os.path.join(rilpath, "modules")):
    for file in files:
        if not file.endswith(".py") or file.startswith("__"):
            continue
        module = ".".join(
            (re.sub(r"[^>]+AsakiConsole/", "",
                    path).replace("/", "."), file[:-3])
        )
        if module.endswith("IE"):
            name = file[:-5]
            module_ = importlib.import_module(module)
            vars.append(name)
            globals()[name] = getattr(module_, file[:-5])

exec(compile(f"""
class Loader(CustomCmd, {", ".join(vars)}):
    pass
""", __name__, "exec"))

run = False
th.join()

separator = '-' * 40
awesome_intro = f'''{APP_NAME} framework {APP_VERSION}

{separator}
{{0.modules}} modules loaded. in total there are {{0.commands}} commands and {{0.auxilaries}} auxilaries.
use the 'help' command to display the menu.
{separator}
'''

del loading
del th
del run
del rilpath
del vars
