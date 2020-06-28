from .base import BaseEngine
from urllib.parse import urlencode

class EcosiaSearch(BaseEngine):
    base_url = "https://www.ecosia.org"
    search_url = "https://www.ecosia.org/search?"

    def get_params(self, query, **params):
        self.params = {
            "q": query,
            "p": 0
        }
        return self.params

    def next_url(self, soup):
        self.params["p"] += 1
        return self.search_url + urlencode(self.params)

    def parse_soup(self, soup):
        for a in soup.find_all("a", class_="result-url"):
            yield a.get("href")
