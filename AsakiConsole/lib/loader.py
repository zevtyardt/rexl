import sys
import os

from lib.constants import APP_VERSION
alternative_app_name = os.path.basename(sys.argv[0])

separator = '-' * 40
awesome_intro = f"""{alternative_app_name} {APP_VERSION}

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
        sys.stdout.write(f"\x1b[K[{next(chars)}] starting {alternative_app_name} framework at {time.strftime('%c')}\r")
        time.sleep(0.2)
    sys.stdout.write("\x1b[K")

import threading
th = threading.Thread(target=loading)
th.daemon = True
th.start()

# importing module
from lib.core import CustomCmd
from typing import Union, Optional

from modules.social_media.fbgraph import FacebookGraph
from modules.lookup.hacker_target import HackerTargetApi
from modules.auxilary import Auxilary
from modules.searchengine import url_crawler

run = False
th.join()

del loading
del th
del run
