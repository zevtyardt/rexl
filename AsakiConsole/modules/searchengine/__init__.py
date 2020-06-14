import argparse

from .engines.aol import AolSearch
from .engines.ask import AskSearch
from .engines.baidu import BaiduSearch
from .engines.bing import BingSearch
from .engines.stackoverflow import StackoverflowSearch
from .engines.yahoo import YahooSearch
from .engines.yandex import YandexSearch
from .engines.youtube import YoutubeSearch
from .engines.google import GoogleSearch
from .engines.startpage import StartpageSearch
from .engines.ecosia import EcosiaSearch
from lib.decorators import with_argparser

class url_crawler:
    BaseParser = argparse.ArgumentParser()
    BaseParser.add_argument("query", nargs="+",  help="search query")
    BaseParser.add_argument("-s", "--stop", dest="stop", metavar="int", help="last result to retrieve", default=float("inf"), type=int)
    BaseParser.add_argument("-d", "--delay", dest="sleep", metavar="int", type=int, help="delay in seconds", default=2)

    def parse_params(self, params):
        dict = params.__dict__
        dict["query"] = " ".join(params.query)
        del dict["__statement__"]
        return dict

    def wrapper(self, class_, params):
        kwargs = self.parse_params(params)
        for pagenum, pageiter in class_.scrape(**kwargs):
            for num, url in pageiter:
                self.poutput(url)

    @with_argparser(BaseParser)
    def do_aol__search_engine__crawler(self, params):
        """url: https://search.aol.com/"""
        aol = AolSearch()
        self.wrapper(aol, params)

    @with_argparser(BaseParser)
    def do_ask__search_engine__crawler(self, params):
        """url: https://www.ask.com"""
        ask = AskSearch()
        self.wrapper(ask, params)

    @with_argparser(BaseParser)
    def do_baidu__search_engine__crawler(self, params):
        """url: https://www.baidu.com"""
        baidu = BaiduSearch()
        self.wrapper(baidu, params)

    @with_argparser(BaseParser)
    def do_bing__search_engine__crawler(self, params):
        """url: https://www.bing.com"""
        bing = BingSearch()
        self.wrapper(bing, params)

    @with_argparser(BaseParser)
    def do_stackoverflow__search_engine__crawler(self, params):
        """url: https://stackoverflow.com"""
        stackoverflow = StackoverflowSearch()
        self.wrapper(stackoverflow, params)

    @with_argparser(BaseParser)
    def do_yahoo__search_engine__crawler(self, params):
        """url: https://search.yahoo.com"""
        yahoo = YahooSearch()
        self.wrapper(yahoo, params)

    @with_argparser(BaseParser)
    def do_yandex__search_engine__crawler(self, params):
        """url: https://yandex.com"""
        yandex = YandexSearch()
        self.wrapper(yandex, params)

    @with_argparser(BaseParser)
    def do_youtube__search_engine__crawler(self, params):
        """url: https://youtube.com"""
        youtube = YoutubeSearch()
        self.wrapper(youtube, params)

    @with_argparser(BaseParser)
    def do_google__search_engine__crawler(self, params):
        """url: https://www.google.com"""
        google = GoogleSearch()
        self.wrapper(google, params)

    @with_argparser(BaseParser)
    def do_startpage__search_engine__crawler(self, params):
        """url: https://www.startpage.com"""
        startpage = StartpageSearch()
        self.wrapper(startpage, params)

    @with_argparser(BaseParser)
    def do_ecosia__search_engine__crawler(self, params):
        """url: https://www.ecosia.org"""
        ecosia = EcosiaSearch()
        self.wrapper(ecosia, params)

