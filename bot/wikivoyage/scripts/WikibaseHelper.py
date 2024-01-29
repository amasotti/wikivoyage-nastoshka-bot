# wikidata_bot.py
import re

import pywikibot
from pywikibot import ItemPage
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

# --- Wikidata properties ---
IS_INSTANCE_OF = 'P31'
IS_DISAMBIGUATION = 'Q4167410'
COORDINATES = 'P625'


class WikibaseHelper:
    def __init__(self):
        self.site = pywikibot.Site().data_repository()

    def get_p_values(self, wikidata_item: ItemPage, p: str):
        item_dict = wikidata_item.get()
        claims = item_dict["claims"]
        if p in claims:
            return [claim.getTarget().title() for claim in claims[p]]
        return []

    def is_disambiguation(self, wikidata_item):
        """
        Check if the given wikidata item is a disambiguation page
        :param wikidata_item:
        :return:
        """
        item = pywikibot.ItemPage(site=self.site, title=wikidata_item)
        item_dict = item.get()
        claims = item_dict["claims"]
        if IS_INSTANCE_OF in claims:
            for claim in claims[IS_INSTANCE_OF]:
                if claim.getTarget().title() == IS_DISAMBIGUATION:
                    return True
        return False

    @staticmethod
    def _truncate_coordinates(coords):
        return tuple(format(x, '.6g') for x in coords)

    def get_coords(self, wikidata_entity : ItemPage):
        item_dict = wikidata_entity.get()
        claims = item_dict["claims"]
        coords = {"lat": None, "long": None}
        if COORDINATES in claims:
            for claim in claims[COORDINATES]:
                raw_coords = claim.getTarget().lat, claim.getTarget().lon
                coords["lat"] = format(raw_coords[0], '.6g')
                coords["long"] = format(raw_coords[1], '.6g')
        return coords

    def get_lat_long(self, wikidata_label):
        """
        Get the latitude and longitude of a given wikidata item
        :param wikidata_label:
        :return:
        """
        item = pywikibot.ItemPage(site=self.site, title=wikidata_label)
        item_dict = item.get()
        claims = item_dict["claims"]
        coords = (None, None)
        if COORDINATES in claims:
            for claim in claims[COORDINATES]:
                coords = claim.getTarget().lat, claim.getTarget().lon

                # Preserve only 6 digits in total for lat and long
                coords = self._truncate_coordinates(coords)
        return coords

    def _clean_city_name(self, city_name):
        """
        Clean the city name from brackets or alternative names
        It could be found in the wikitext in the following formats:
        - [[City name]] -- remove the brackets
        - [[City name|Alt name]] -- remove the brackets and the alternative name
        - City Name -- keep as it is
        :param city_name: City name to clean
        :return: The cleaned city name
        """
        # Remove brackets
        city_name = city_name.strip()

        if city_name.startswith("[[") and city_name.endswith("]]"):
            city_name = city_name.replace("[[", "").replace("]]", "")

        # Remove alternative names
        city_name = re.sub(r'\|.*', '', city_name)

        return city_name

    def get_wikidata_entity_by_wikipedia_article_name(self, article_name: str, alt: str, lang='it') -> str:
        # Try languages in the given order until we find one
        for attempted_lang in [lang, 'en']:
            wikidata_item = self.try_entity_retrieval(article_name, attempted_lang)
            if wikidata_item:
                break
        # Lastly, try alt name in English if entity is still not found
        if not wikidata_item:
            wikidata_item = self.try_entity_retrieval(alt, 'en')
        return self.finalize_wikidata_item(wikidata_item, article_name)

    def try_entity_retrieval(self, article_name, lang) -> str | None:
        item: str | None = self.run_query_for_label(article_name, lang, limit=1)  # limit=1 to avoid multiple results
        return item if item else None

    def finalize_wikidata_item(self, wikidata_item: str, article_name: str) -> str:
        if not wikidata_item:
            print(f"\t\tCould not find wikidata item for {article_name} -- keeping empty")
            return ""
        elif self.is_disambiguation(wikidata_item):
            self.write_log_line(f"Wikidata item for {article_name} is a disambiguation page\n")
            return ""
        else:
            return wikidata_item

    def run_query(self, query) -> WikidataSPARQLPageGenerator:
        """
        Run a query on wikidata
        :param query:
        :return:
        """
        gen = WikidataSPARQLPageGenerator(
            query,
            site=self.site,
            endpoint='https://query.wikidata.org/sparql'
        )
        return gen

    def run_query_for_label(self, entity_label, lang='it', limit=1) -> str | list[str] | None:
        """
        Get the Wikidata item for a city if a corresponding wp article in italian or english exists
        :param limit:  if 1, return only the first result, else return a list of results
        :param entity_label: the city name
        :param lang: the language of the city name to search wikipedias for
        :return:
        """

        entity_label = self._clean_city_name(entity_label)

        query = f"""
        SELECT ?item WHERE {{
          ?sitelink schema:about ?item;
            schema:isPartOf <https://{lang}.wikipedia.org/>;
            schema:name "{entity_label}"@{lang}.
        }}"""

        gen = WikidataSPARQLPageGenerator(
            query,
            site=self.site,
            endpoint='https://query.wikidata.org/sparql'
        )
        # make sure that the generator is not empty and is of length 1
        # (otherwise we have a problem)
        pages = list(gen)

        if limit == 1:
            if len(pages) != 1:
                print(f"\tFound zero or multiple wikidata item for {entity_label} -- skipping")
                return None
            return pages[0].title()
        else:
            return [page.title() for page in pages]

    def get_iso_3166_1_from_city(self, city_entity):
        # Get the country of the city (P17)
        country = self.get_country_from_city(city_entity)

        # Get the iso 3166-1 code of the country (P297)
        item = pywikibot.ItemPage(site=self.site, title=country)
        item_dict = item.get()
        claims = item_dict["claims"]
        if "P297" in claims:
            for claim in claims["P297"]:
                return claim.getTarget().title()
        elif "P300" in claims:
            for claim in claims["P300"]:
                return claim.getTarget().title()
        return None

    def write_log_line(self, text, file="logs/citylist_log.log"):
        """
        Write a line to the log file
        :param text: the log line
        :param file: the log file
        :return: None
        """
        with open(file, 'a') as f:
            f.write(text)
            f.close()

    def get_image(self, wikidata_entity: ItemPage):
        """
        Get the image of a given wikidata item
        :param wikidata_entity:
        :return:
        """
        item_dict = wikidata_entity.get()
        claims = item_dict["claims"]
        if "P18" in claims:
            for claim in claims["P18"]:
                return claim.getTarget().title()
        return None


    def get_country_from_city(self, city_entity):
        """
        Get the country of a city
        :param city_entity:
        :return:
        """
        item_dict = city_entity.get()
        claims = item_dict["claims"]
        if "P17" in claims:
            for claim in claims["P17"]:
                return claim.getTarget().title()
        return None
