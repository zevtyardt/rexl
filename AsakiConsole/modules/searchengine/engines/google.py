from .base import BaseEngine
import re
import bs4

class GoogleSearch(BaseEngine):
    base_url = "https://www.google.com"
    search_url = "https://www.google.com/search"

    def get_params(self, query, **params):
        return {"q": query, "start": 0}

    def next_url(self, soup):
        next_url = None
        if (pnnext := soup.find(id="pnnext")):
            next_url = pnnext.attrs["href"]
        elif (regex := re.findall(r'"(/search[^>]+start[^"]+)', str(soup))):
            next_url = regex[-1]
        if next_url:
            return self.base_url + next_url

    def parse_soup(self, soup):
        s_s = str(soup)
        for url in soup.find_all(class_="g") or soup.find_all(class_="r") or re.findall(r"/url\?q=([^&]+)", s_s):
            if isinstance(url, bs4.element.Tag):
                url = url.a.get("href", "google.")
            if "google." not in url:
                yield url

    def captcha(self, response):
        return "Our systems have detected unusual traffic from your computer network." in response.text and "/sorry" in response.url
