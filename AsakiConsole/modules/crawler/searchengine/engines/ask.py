from .base import BaseEngine
import re


class AskSearch(BaseEngine):
    base_url = "https://www.ask.com"
    search_url = "https://www.ask.com/web"

    def get_params(self, query, **params):
        params["o"] = 0
        params["l"] = "dir"
        params["qo"] = "pagination"
        params["q"] = query
        params["qsrc"] = 998
        return params

    def next_url(self, soup):
        if (regex := re.findall(r'"(/web\?[^>]+page[^"]+)', str(soup))):
            return self.base_url + regex[-1]

    def parse_soup(self, soup):
        for raw in soup.find_all('div', class_="PartialSearchResults-item"):
            if (url := raw.a.get("href")):
                yield url
