from .base import BaseEngine
import re


class BaiduSearch(BaseEngine):
    base_url = "https://www.baidu.com"
    search_url = "https://www.baidu.com/s"

    def get_params(self, query, **params):
        params["wd"] = query
        params["oq"] = query
        return params

    def next_url(self, soup):
        if (regex := re.findall(r'"(/s\?[^>]+pn=\d+[^"]+)', str(soup))):
            return self.base_url + regex[-1]

    def parse_soup(self, soup):
        for raw in soup.find_all('div', {'id': re.compile(r"^\d{1,2}")}):
            if (url := raw.a.get("href")):
                yield url
