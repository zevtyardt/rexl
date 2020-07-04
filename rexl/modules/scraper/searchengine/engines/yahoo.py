from .base import BaseEngine
import urllib.parse
import re

class YahooSearch(BaseEngine):
    base_url = "https://search.yahoo.com"
    search_url = "https://search.yahoo.com/search"

    def get_params(self, query, **params):
        return {"p": query}

    def next_url(self, soup):
        if (next := soup.find(class_="next")):
            return next["href"]

    def parse_soup(self, soup):
        for tag in soup.find_all("div", class_="Sr"):
            if (rawurl := re.search(r"RU=([^/]+)", str(tag))):
                yield urllib.parse.unquote(rawurl.group(1))
