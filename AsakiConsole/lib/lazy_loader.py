from lib.core import CustomCmd
from lib.constants import APP_VERSION, APP_NAME
import threading
import sys
import time
import os

run = True
msg = None
vars = []


def loading():
    global msg
    import itertools

    chars = itertools.cycle([
        "....", "...", "..", ".", "..", "..."
    ])
    while run:
        if vars:
            klass = globals().get(vars[-1])
            message = f"{klass.__module__} loaded"
            msg = None
        elif msg:
            message = msg
        else:
            message = f"Initializing"
        sys.stdout.write(
            f"\x1b[K  {message} {next(chars)}\r")
        time.sleep(0.2)
    sys.stdout.write("\x1b[K")


th = threading.Thread(target=loading)
th.daemon = True
th.start()

# start
# ~~~~~

import git
import importlib
import re

project_url = "https://github.com/zevtyardt/asaki"


def lsremote(url):
    global msg
    remote_refs = {}
    try:
        g = git.cmd.Git()
        for ref in g.ls_remote(url).split('\n'):
            hash_ref_list = ref.split('\t')
            remote_refs[hash_ref_list[1]] = hash_ref_list[0]
    except git.exc.GitCommandError:
        msg = "failed to get the last commit"
    return remote_refs


def update_framework():
    global msg

    msg = "check the latest version"
    repo = git.Repo(search_parent_directories=True)
    current = repo.head.object.hexsha
    if current != lsremote(project_url).get("HEAD", current):
        msg = "updating framework"
        repo.remotes.origin.pull()
    else:
        msg = "framework is the latest version"


update_framework()

rilpath = sys.path[1]
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
del msg
