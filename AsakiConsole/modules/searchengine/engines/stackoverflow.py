from .base import BaseEngine
import re


class StackoverflowSearch(BaseEngine):
    base_url = "https://stackoverflow.com"
    search_url = base_url + "/search"

    def get_params(self, query, **params):
        params["q"] = query
        return params

    def next_url(self, soup):
        if (regex := re.findall(r'"(/search\?[^>]*page=[^"]+)', str(soup))):
            return self.base_url + regex[-1]

    def parse_soup(self, soup):
        for raw in soup.find_all('div', class_="summary"):
            if (url := raw.a.get("href")):
                yield self.base_url + url[:url.find("?")]

    def captcha(self, response):
        return "nocaptcha" in response.url
