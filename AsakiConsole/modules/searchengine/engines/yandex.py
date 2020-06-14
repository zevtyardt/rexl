from .base import BaseEngine
import re


class YandexSearch(BaseEngine):
    base_url = "https://yandex.com"
    search_url = "https://yandex.com/search/"

    def get_params(self, query, **params):
        params["text"] = query
        params["p"] = None
        return params

    def next_url(self, soup):
        if (regex := re.findall(r'"(/search/\?[^>]+p=[^"]+)', str(soup))):
            return self.base_url + regex[-1]

    def parse_soup(self, soup):
        for raw in soup.find_all('li', class_="serp-item"):
            if (url := raw.a.get("href")):
                yield url

    def captcha(self, response):
       return "showcaptcha" in response.url
