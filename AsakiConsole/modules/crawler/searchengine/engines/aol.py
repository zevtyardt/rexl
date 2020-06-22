from .base import BaseEngine
import re
import urllib.parse

class AolSearch(BaseEngine):
    base_url = "https://search.aol.com/"
    search_url = "https://search.aol.com/aol/search"

    def get_params(self, query, **params):
        return {"q": query}

    def next_url(self, soup):
        if (next := soup.find(class_="next")):
            return next["href"]

    def parse_soup(self, soup):
        for tag in soup.find_all("div", class_="algo-sr"):
            if (rawurl := re.search(r"RU=([^/]+)", str(tag))):
                yield urllib.parse.unquote(rawurl.group(1))
