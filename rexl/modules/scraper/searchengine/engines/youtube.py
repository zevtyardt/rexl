from .base import BaseEngine
import re


class YoutubeSearch(BaseEngine):
    base_url = "https://youtube.com"
    search_url = base_url + "/results?"

    def parse_soup(self, soup):
        for raw in soup.find_all('div', class_='yt-lockup-content'):
            for link in re.findall(r"/watch\?[^&\"]+", str(raw)):
                yield self.base_url + link

