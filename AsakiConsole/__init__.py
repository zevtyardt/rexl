import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lib.lazy_loader import Loader, awesome_intro

class Asaki(Loader):
    def __init__(self):
        super().__init__()
        self.prompt = "sk"
        self.intro = awesome_intro.format(
            len(self.modules), self._total_commands, self._auxilary
        )
        self._add_settable("facebook_user_access_token",
                           str, "Facebook user access token.")

def main():
    sys.argv = sys.argv[:1]

    flow = Asaki()
    flow.cmdloop()

if __name__ == "__main__":
    x = main()
