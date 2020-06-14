from .base import BaseEngine

class StartpageSearch(BaseEngine):
    base_url = "https://www.startpage.com"
    search_url = "https://www.startpage.com/sp/search"

    def get_params(self, query, **params):
        return {"data": {
          "query": query,
          "cat": "web",
        }}

    def parse_soup(self, soup):
        for raw in soup.find_all(class_="w-gl__result-url"):
            yield raw.get("href")

    def next_url(self, soup):
        if (form := soup.findAll("form")):
            form = form[-1]
            if form.button.text.strip() == "Next":
                data = self.get_all_input(form)
                return self.search_url, {"data": data}
