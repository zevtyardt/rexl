import requests
import itertools
import os
import re
import random
import bs4
import sys
from http.cookiejar import LWPCookieJar
from cmd2 import ansi
import time

class BaseEngine(object):
    base_url = "https://example.com"
    search_url = "https://example.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.cookies = LWPCookieJar()
        self.add_headers({
            "User-Agent": self._random_user_agent
        })

    def add_headers(self, d: dict) -> None:
        self.session.headers.update(d)

    @property
    def _random_user_agent(self) -> str:
        return random.choice([
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; pt-BR) AppleWebKit/533.3 '
            '(KHTML, like Gecko)  QtWeb Internet Browser/3.7 http://www.QtWeb.net',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/41.0.2228.0 Safari/537.36',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, '
            'like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4pre) '
            'Gecko/20070404 K-Ninja/2.1.3',
            'Mozilla/5.0 (Future Star Technologies Corp.; Star-Blade OS; x86_64; U; '
            'en-US) iNet Browser 4.7',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) '
            'Gecko/20080414 Firefox/2.0.0.13 Pogo/2.0.0.13.6866',
        ])

    def load(self, cookie_file: str) -> None:
        self.session.cookies.load(cookie_file)

    def save(self, cookie_file: str, pwd: bool = False) -> None:
        if pwd:
            cookie_file = os.path.join(os.path.dirname(__file__), cookie_file)
        self.session.cookies.save(cookie_file)

    def _download_webpage(self, url: str, **params) -> requests.Response:
        if params.get("data"):
            return self.session.post(url, **params)
        else:
            return self.session.get(url	, **params)

    def _get_soup(self, url: str, **params) -> "bs4.element.ResultSet":
        self.response = self._download_webpage(url, **params)
        return bs4.BeautifulSoup(self.response.text, "html.parser")

    # Hooks Method
    def preloop(self, query, **params) -> None:
        """hook method before the loop starts."""
        self.session.get(self.base_url)

    def get_params(self, query, **params) -> dict:
        """set up parameters"""
        return {}

    def next_url(self, soup: bs4.BeautifulSoup) -> "full url":
        """make preparations to the next url"""
        return ""

    def parse_soup(self, soup: bs4.BeautifulSoup) -> iter:
        """take all the urls on the page"""
        return iter([])

    def captcha(self, response: requests.Response) -> bool:
        """is page got captcha"""
        return re.search(r'(?:re)?chaptcha(?:.min.js)?', response.text)

    def perror(self, msg: str = '', *, end: str = '\n', apply_style: bool = True) -> None:
        if apply_style:
            final_msg = ansi.style_error(msg)
        else:
            final_msg = "{}".format(msg)
        ansi.style_aware_write(sys.stderr, final_msg + end)

    def poutput(self, msg: str = "", *, end: str = "\n") -> None:
        ansi.style_aware_write(sys.stdout, "{}{}".format(msg, end))

    def _validate_url(self, url: str, tlds_list: list = []) -> bool:
        return url.startswith("http")

    def _next_url(self, html: bs4.BeautifulSoup) -> "url, params":
        if (raw := self.next_url(html)):
            if len(raw) != 2:
                raw = (raw, {})
            return raw
        return None, {}

    def sleep(self, count: int):
        while count > 0:
            self.poutput("\x1b[KINFO: sleeping for %s seconds\r" % count, end="")
            time.sleep(1)
            count -= 1
        self.poutput("\x1b[K", end="")

    def get_all_input(self, form: bs4.element.Tag) -> dict:
        d = {}
        for input in form.find_all("input"):
            if (name := input.get("name")) and (value := input.get("value")):
                d[name] = value
        return d

    def scrape(self, query: str, stop: int = float("inf"), sleep: int = 2,
               tlds_list: list = [],  **params: any) -> iter:
        hashes = set()
        self.preloop(query, **params)
        url, params = self.search_url, self.get_params(query, **params)

        def _filter_urls(urls: list) -> iter:
            for url in urls:
                if len(hashes) >= stop:
                    break
                url = url.replace("&amp;", "&")

                # only yield unique url
                if url not in hashes and self._validate_url(url, tlds_list=tlds_list):
                    hashes.add(url)
                    yield len(hashes), url

        page = 1
        got_captcha = None
        while len(hashes) < stop and url:
            if not params.get("data"):
                params = {"params": params}
            url = url.replace("&amp;", "&")
            html = self._get_soup(url, **params)
            if (got_captcha := self.captcha(self.response)):
                self.perror("Our systems have detected unusual traffic from your computer network.")
                break
            raw_urls = self.parse_soup(html)
            unique_urls, new_iter = itertools.tee(_filter_urls(raw_urls))
            if sum(1 for _ in new_iter) <= 0:
                break
            # final result
            yield page, unique_urls  # yield per - page
            # update url and params
            url, params = self._next_url(html)
            page += 1

            if len(hashes) < stop:
                self.sleep(sleep)

        if not hashes and not got_captcha:
            self.perror("%s - does not match any documents." % query)
        # remove all elements
        hashes.clear()

