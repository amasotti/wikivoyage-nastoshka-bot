import pywikibot

from bot.GeneralBot import WikiBot

DESTINATION_TEMPLATE_ITEM_NAME = "Destinazione"
CITY_TEMPLATE_ITEM_NAME = "Città"

class WikivoyageBot(WikiBot):
    def __init__(self, lang="it"):
        super().__init__(lang, fam="wikivoyage")

    def listify_category(self, cat_name):
        category = pywikibot.Category(self.site, title=cat_name)
        return list(category.articles(total=4))

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
