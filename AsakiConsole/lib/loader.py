import sys
import os

from lib.constants import APP_VERSION, APP_NAME, AUTHOR_USERNAME

separator = '-' * 40
awesome_intro = f"""{APP_NAME} framework {APP_VERSION} {AUTHOR_USERNAME}

{separator}
{{}} modules loaded. in total there are {{}} commands and {{}} auxilaries.
use the 'help' command to display the menu.
{separator}
"""

run = True
def loading():
    import itertools
    import time

    chars = itertools.cycle(r"\|/-")
    while run:
        sys.stdout.write(f"\x1b[K[{next(chars)}] starting {APP_NAME} framework at {time.strftime('%c')}\r")
        time.sleep(0.2)
    sys.stdout.write("\x1b[K")

import threading
th = threading.Thread(target=loading)
th.daemon = True
th.start()

# importing module
from lib.core import CustomCmd

from modules.social_media.fbgraph import FacebookGraph
from modules.lookup import Lookup
from modules.auxilary import Auxilary
from modules.searchengine import url_crawler

class MainModule(CustomCmd, FacebookGraph, Lookup, Auxilary, url_crawler):
    pass

run = False
th.join()

del loading
del th
del run
