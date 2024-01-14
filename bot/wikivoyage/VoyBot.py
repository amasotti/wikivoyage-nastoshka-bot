from datetime import datetime
import pywikibot
from bot.GeneralBot import WikiBot
from bot.wikidata import WikidataBot
from bot.wikivoyage.constants import DESTINATION_TEMPLATE_ITEM_NAME, CITY_TEMPLATE_ITEM_NAME


class WikivoyageBot(WikiBot):
    def __init__(self, lang="it"):
        super().__init__(lang, fam="wikivoyage")
        self.current_page = None

    def set_current_page(self, page):
        self.current_page = page

    def get_page_text(self, p_name):
        page = pywikibot.Page(self.site, title=p_name, ns=0)
        return page.text

    def listify_category(self, cat_name, total=4):
        category = pywikibot.Category(self.site, title=cat_name)
        return list(category.articles(recurse=True, total=total))

    def get_page_templates(self, p_name):
        page = pywikibot.Page(self.site, title=p_name, ns=0)
        return page.templatesWithParams()

    def get_pages_using_template(self, template_name, total=3):
        template_page = pywikibot.Page(self.site, title=template_name, ns=10)
        linked_pages = template_page.getReferences(
            namespaces=0,
            total=total,
            only_template_inclusion=True)
        return list(linked_pages)

    def parse_listed_destinations(self, wikitext):
        return self.parse_nested_template(wikitext, DESTINATION_TEMPLATE_ITEM_NAME)

    def parse_listed_cities(self, wikitext):
        return self.parse_nested_template(wikitext, CITY_TEMPLATE_ITEM_NAME)

    def process_wikidata_in_citylist(self, templates):
        wd_bot = WikidataBot()
        for template in templates:
            # Conditions
            is_target_template = (template.name == CITY_TEMPLATE_ITEM_NAME
                                  or template.name == DESTINATION_TEMPLATE_ITEM_NAME)
            has_wikidata = template.has("wikidata")

            if is_target_template and not has_wikidata:
                name = template.get("nome").value.strip()
                alt = template.get("alt").value.strip()
                wikidata_id = wd_bot.get_wikidata_entity_by_wikipedia_article_name(name, alt, lang='it')
                self._process_wikidata(name, wikidata_id, template)
        return templates

    def _process_wikidata(self, name, wikidata_id, template):
        if wikidata_id == "":
            pywikibot.logging.stdout(f"\tCould not find wikidata item for {name} -- keeping empty")
            self.write_log_line(f"{self.current_page} -- No wikidata item found for {name}")
        else:
            pywikibot.logging.stdout(f"\tFound wikidata item for {name}: {wikidata_id}")
            template.add("wikidata", wikidata_id)

    def write_log_line(self, text, file="logs/citylist_log.txt"):
        with open(file, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {text}\n")
