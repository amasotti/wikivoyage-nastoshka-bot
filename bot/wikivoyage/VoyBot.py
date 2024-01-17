from datetime import datetime

import pywikibot

from bot.GeneralBot import WikiBot
from bot.wikidata import WikidataBot
from bot.wikivoyage.constants import DYNAMIC_MAP_TEMPLATE


def write_log_line(text, file="logs/citylist_log.log", with_timestamp=True):
    """
    Write a line to the log file
    :param text: the log line
    :param file: the log file
    :return: None
    """
    with open(file, "a") as f:
        if with_timestamp:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {text}\n")
        else:
            f.write(f"{text}\n")


class WikivoyageBot(WikiBot):
    def __init__(self, lang="it"):
        super().__init__(lang, fam="wikivoyage")
        self.current_page = None
        self.wd_bot = WikidataBot()

    def set_current_page(self, page):
        """
        Set the current page, to be then used in logging
        :param page:
        :return:
        """
        self.current_page = page

    def is_in_category(self, page_name, category):
        """
        Check if a page is in a category
        :param page:
        :param category:
        :return:
        """
        page = self.get_page(page_name)
        cats = [x.title() for x in page.categories()]
        return category in cats

    def process_dynamicMap_without_coordinates(self, templates):
        """
        Add wikidata ids to the citylist templates if they are missing and can be found, updating the
        templates in place
        :param templates:
        :return:
        """
        for template in templates:
            # Conditions (We iterate a category that is supposed to contain only dynamic maps without coordinates)
            if template.name == DYNAMIC_MAP_TEMPLATE:
                page = self.get_page(self.current_page)
                wikidata_id = page.data_item()
                pywikibot.logging.info(f"Found wikidata item for {self.current_page}: {wikidata_id.title()}")
                coords = self.wd_bot.get_lat_long(wikidata_id.title())

                if coords[0] is None:
                    pywikibot.logging.stdout(f"\tCould not find coordinates for {self.current_page} -- keeping empty")
                    write_log_line(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {self.current_page} -- No coordinates updated",
                        file="logs/dynamic_map_log.log")
                else:
                    pywikibot.logging.stdout(f"\tFound coordinates for {self.current_page}: {coords}")
                    template.add("Lat", str(" " + coords[0]), before="h", preserve_spacing=True)
                    template.add("Long", str(" " + coords[1]), before="h", preserve_spacing=True)

                    # More or less an informed guess, needs to be checked
                    if self.is_in_category(self.current_page, "Categoria:Città"):
                        template.add("z", "12", preserve_spacing=True)
                    elif self.is_in_category(self.current_page, "Categoria:Regione"):
                        template.add("z", "6", preserve_spacing=True)
                    elif self.is_in_category(self.current_page, "Categoria:Distretto"):
                        template.add("z", "10", preserve_spacing=True)
                    elif self.is_in_category(self.current_page, "Categoria:Parco") or self.is_in_category(
                            self.current_page, "Categoria:Sito archeologico"):
                        template.add("z", "10", preserve_spacing=True)

                    write_log_line(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {self.current_page} -- Added coordinates",
                        file="logs/dynamic_map_log.log")
        return templates
