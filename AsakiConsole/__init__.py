import sys
import cmd2
import os
import argparse


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("commands", metavar="command", nargs="*", help="execute the command and exit.")
    parser.add_argument("-k", "--keep-running", dest="keep_running", action="store_true", help="keep running `cmdloop`")
    return parser

parser = make_parser()
args = parser.parse_args()

sys.path.insert(0, os.path.dirname(__file__))
from lib.lazy_loader import Loader, awesome_intro

class Asaki(Loader):
    def __init__(self):
        super().__init__()
        self.prompt = f"sk"
        self.intro = awesome_intro.format(self.total)

        self._add_settable("facebook_user_access_token",
                           str, "Facebook user access token.")

def main():
    sys.argv = sys.argv[:1]
    flow = Asaki()
    if args.commands:
        for command in args.commands:
            try:
                flow.poutput(f"Executing command: {command}")
                flow.onecmd(command)
            except cmd2.exceptions.Cmd2ArgparseError:
                pass
    if args.keep_running or not args.commands:
        flow.cmdloop()

if __name__ == "__main__":
    main()
