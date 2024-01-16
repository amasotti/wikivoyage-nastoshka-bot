from datetime import datetime
import pywikibot
from bot.GeneralBot import WikiBot
from bot.wikidata import WikidataBot
from bot.wikivoyage.constants import DESTINATION_TEMPLATE_ITEM_NAME, CITY_TEMPLATE_ITEM_NAME, DYNAMIC_MAP_TEMPLATE


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

    def parse_listed_destinations(self, wikitext):
        """
        Parse the destinationlist template in the given wikitext
        :param wikitext:
        :return:
        """
        return self.parse_nested_template(wikitext, DESTINATION_TEMPLATE_ITEM_NAME)

    def parse_listed_cities(self, wikitext):
        """
        Parse the citylist template in the given wikitext
        :param wikitext:
        :return:
        """
        return self.parse_nested_template(wikitext, CITY_TEMPLATE_ITEM_NAME)

    def process_wikidata_in_citylist(self, templates):
        """
        Add wikidata ids to the citylist templates if they are missing and can be found, updating the
        templates in place
        :param templates:
        :return:
        """
        for template in templates:

            # Conditions
            is_target_template = (template.name == CITY_TEMPLATE_ITEM_NAME
                                  or template.name == DESTINATION_TEMPLATE_ITEM_NAME)
            has_wikidata = template.has("wikidata")

            if is_target_template and not has_wikidata:
                name = template.get("nome").value.strip()
                try:
                    alt = template.get("alt").value.strip()
                except:
                    alt = ""
                wikidata_id = self.wd_bot.get_wikidata_entity_by_wikipedia_article_name(name, alt, lang='it')
                # Try to also add coordinates
                self._process_coordinates(name, wikidata_id, template)
                self._process_wikidata(name, wikidata_id, template)
        return templates

    def _process_coordinates(self, name, wikidata_id, template):
        """
        Add the coordinates to the template if they exist. Basically a check that the given coordinates
        are not None. Also logs the operation
        :param name: str, the name of the city
        :param wikidata_id: str, the wikidata id of the city
        :param template: the template to update
        :return: None (updates the template in place)
        """
        if wikidata_id == "" or wikidata_id is None:
            return None

        coords = self.wd_bot.get_lat_long(wikidata_id)
        if coords[0] is None:
            pywikibot.logging.stdout(f"\tCould not find coordinates for {name} -- keeping empty")
        else:
            pywikibot.logging.stdout(f"\tFound coordinates for {name}: {coords}")
            template.add("lat", coords[0], before="descrizione", preserve_spacing=True)
            template.add("long", coords[1], before="descrizione", preserve_spacing=True)

    def _process_wikidata(self, name, wikidata_id, template):
        """
        Add the wikidata id to the template if it exists. Basically a check that the given wikidata id
        is not an empty string. Also logs the operation
        :param name:
        :param wikidata_id:
        :param template:
        :return:
        """
        if wikidata_id == "":
            pywikibot.logging.stdout(f"\tCould not find wikidata item for {name} -- keeping empty")
            self.write_log_line(f"{self.current_page} -- No wikidata item found for {name}")
        else:
            pywikibot.logging.stdout(f"\tFound wikidata item for {name}: {wikidata_id}")
            template.add("wikidata", wikidata_id, before="descrizione", preserve_spacing=True)

    def write_log_line(self, text, file="logs/citylist_log.log", with_timestamp=True):
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
                    self.write_log_line(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {self.current_page} -- No coordinates updated",
                        file="logs/dynamic_map_log.log"
                    )
                else:
                    pywikibot.logging.stdout(f"\tFound coordinates for {self.current_page}: {coords}")
                    template.add("Lat", str(" " + coords[0]), before="h", preserve_spacing=True)
                    template.add("Long", str(" " + coords[1]), before="h", preserve_spacing=True)

                    # More or less an informed guess, needs to be checked
                    if self.is_in_category(self.current_page,"Categoria:Città"):
                        template.add("z", "12", preserve_spacing=True)
                    elif self.is_in_category(self.current_page,"Categoria:Regione"):
                        template.add("z", "6", preserve_spacing=True)
                    elif self.is_in_category(self.current_page,"Categoria:Distretto"):
                        template.add("z", "10", preserve_spacing=True)
                    elif self.is_in_category(self.current_page,"Categoria:Parco") or self.is_in_category(self.current_page,"Categoria:Sito archeologico"):
                        template.add("z", "10", preserve_spacing=True)

                    self.write_log_line(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {self.current_page} -- Added coordinates",
                        file="logs/dynamic_map_log.log"
                    )
        return templates
