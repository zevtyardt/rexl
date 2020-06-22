from lib.constants import APP_VERSION, APP_NAME, AUTHOR_USERNAME
import threading
import sys

run = True
def loading():
    import itertools
    import time

    chars = itertools.cycle(r"\|/-")
    while run:
        sys.stdout.write(
            f"\x1b[K[{next(chars)}] starting {APP_NAME} framework at {time.strftime('%c')}\r")
        time.sleep(0.2)
    sys.stdout.write("\x1b[K")

th = threading.Thread(target=loading)
th.daemon = True
th.start()

from lib.core import CustomCmd
import os
import re
import importlib

separator = '-' * 40
awesome_intro = f'''{APP_NAME} framework {APP_VERSION} {AUTHOR_USERNAME}

{separator}
{{}} modules loaded. in total there are {{}} commands and {{}} auxilaries.
use the 'help' command to display the menu.
{separator}
'''

rilpath = sys.path[0]
vars = []
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

del loading
del th
del run
del rilpath
del vars
