# wikidata_bot.py
import pywikibot
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator

class WikidataBot:
    def __init__(self):
        self.site = pywikibot.Site().data_repository()

    def _clean_city_name(self, city_name):
        return city_name.replace("[", "").replace("]", "").strip()

    def get_wikidata_entity_by_wikipedia_article_name(self,article_name, alt, lang='it'):

        # Try in italian or the language passed
        wikidata_item = self.run_query(article_name, lang)

        # If not found, try in english
        if wikidata_item is None:
            wikidata_item = self.run_query(article_name, 'en')

        # One last try with the alt name
        if wikidata_item is None:
            wikidata_item = self.run_query(alt, 'en')

        if wikidata_item is None:
            print(f"\t\tCould not find wikidata item for {article_name} -- keeping empty")
            wikidata_item = ""

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
