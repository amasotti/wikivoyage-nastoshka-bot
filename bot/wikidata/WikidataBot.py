# wikidata_bot.py
import pywikibot
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

class WikidataBot:
    def __init__(self):
        self.site = pywikibot.Site().data_repository()

    def _clean_city_name(self, city_name):
        return city_name.replace("[", "").replace("]", "")

    def get_wikidata_item_for_city(self, city_name, lang='it'):
        """
        Get the Wikidata item for a city if a corresponding wp article in italian or english exists
        :param city_name:
        :param lang:
        :return:
        """

        city_name = self._clean_city_name(city_name)

        query = f"""
        SELECT ?item WHERE {{
          ?sitelink schema:about ?item;
            schema:isPartOf <https://{lang}.wikipedia.org/>;
            schema:name "{city_name}"@{lang}.
        }}"""

        gen = WikidataSPARQLPageGenerator(
            query,
            site=self.site,
            endpoint='https://query.wikidata.org/sparql'
        )
        for page in gen:
            return page.title()  # Returns the Wikidata item ID
        return None
