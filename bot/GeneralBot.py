import pywikibot
from pywikibot import textlib

class WikiBot:
    def __init__(self, lang="it", fam="wikivoyage"):
        self.site = pywikibot.Site(code=lang, fam=fam)

    def get_page_text(self, page_name):
        page = pywikibot.Page(self.site, title=page_name)
        return page.text

    def parse_nested_template(self, wikitext, template_name):
        parsed_data = textlib.extract_templates_and_params(wikitext, True, True)
        return [x for x in parsed_data if x[0] == template_name]
