from .HackerTargetApi import HackerTargetApi
from lib.decorators import with_argparser

import argparse
import requests
import json

class Lookup(HackerTargetApi):
    MacParser = argparse.ArgumentParser()
    MacParser.add_argument("mac", metavar="mac address", help="mac address")

    @with_argparser(MacParser)
    def do_mac_lookup__lookup(self, params):
        """Finds information about a Particular Mac address"""
        resp = requests.get(f"http://macvendors.co/api/{params.mac}").json()
        self.poutput(json.dumps(resp, indent=2))
