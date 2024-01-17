# wikidata_bot.py
import re

import pywikibot
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

# --- Wikidata properties ---
IS_INSTANCE_OF = 'P31'
IS_DISAMBIGUATION = 'Q4167410'
COORDINATES = 'P625'


class WikibaseHelper:
    def __init__(self):
        self.site = pywikibot.Site().data_repository()

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

    def get_lat_long(self, wikidata_item):
        """
        Get the latitude and longitude of a given wikidata item
        :param wikidata_item:
        :return:
        """
        item = pywikibot.ItemPage(site=self.site, title=wikidata_item)
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
        city_name = city_name.replace("[[", "").replace("]]", "")

        # Remove alternative names
        city_name = re.sub(r'\|.*', '', city_name)

        return city_name

    def get_wikidata_entity_by_wikipedia_article_name(self, article_name, alt, lang='it'):
        # Try languages in the given order until we find one
        for attempted_lang in [lang, 'en']:
            wikidata_item = self.try_entity_retrieval(article_name, attempted_lang)
            if wikidata_item:
                break
        # Lastly, try alt name in English if entity is still not found
        if not wikidata_item:
            wikidata_item = self.try_entity_retrieval(alt, 'en')
        return self.finalize_wikidata_item(wikidata_item, article_name)

    def try_entity_retrieval(self, article_name, lang):
        item = self.run_query(article_name, lang)
        return item if item else None

    def finalize_wikidata_item(self, wikidata_item, article_name):
        if not wikidata_item:
            print(f"\t\tCould not find wikidata item for {article_name} -- keeping empty")
            return ""
        elif self.is_disambiguation(wikidata_item):
            self.write_log_line(f"Wikidata item for {article_name} is a disambiguation page\n")
            return ""
        else:
            return wikidata_item

    def run_query(self, entity_label, lang='it'):
        """
        Get the Wikidata item for a city if a corresponding wp article in italian or english exists
        :param entity_label:
        :param lang:
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

        if len(pages) != 1:
            print(f"\tFound zero or multiple wikidata item for {entity_label} -- skipping")
            return None
        return pages[0].title()

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
