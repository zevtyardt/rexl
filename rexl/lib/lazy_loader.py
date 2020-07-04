from lib.core import CustomCmd
from lib.constants import APP_VERSION
import threading
import sys
import time
import os

run = True
vars = []

def loading():
    import itertools

    message = "https://github.com/zevtyardt/rexl"

    index = itertools.cycle(range(len(message)))
    while run:
        i = next(index)
        sys.stdout.write(
            f"\x1b[K  {message[:i] + message[i].upper() + message[i + 1:]}\r"
        )
        time.sleep(0.1)
    sys.stdout.write("\x1b[K")


th = threading.Thread(target=loading)
th.daemon = True
th.start()

# start
# ~~~~~

import importlib
import re

rilpath = sys.path[0]
for path, dirs, files in os.walk(os.path.join(rilpath, "modules")):
    for file in files:
        if not file.endswith(".py") or file.startswith("__"):
            continue
        module = ".".join(
            (re.sub(r"[^>]+rexl/", "",
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
awesome_intro = f''' _____ _____ __ __ __
| __  |   __|  |  |  |
|    -|   __|-   -|  |__
|__|__|_____|__|__|_____| {APP_VERSION}

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
