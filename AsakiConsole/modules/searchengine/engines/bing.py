from .base import BaseEngine


class BingSearch(BaseEngine):
    base_url = "https://www.bing.com"
    search_url = "https://www.bing.com/search"

    def get_params(self, *args, **kwargs):
        return {"q": args[0]}

    def next_url(self, soup):
        if (a := soup.find("a", class_="sb_pagN") or soup.find("a", title="Next page")):
            return self.base_url + a.attrs["href"]
        return ""

    def parse_soup(self, soup):
        for b_algo in soup.findAll(class_="b_algo"):
            if (href := b_algo.a.attrs.get("href")):
                yield href
