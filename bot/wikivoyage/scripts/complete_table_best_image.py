import pywikibot
import mwparserfromhell
from mwparserfromhell.nodes import Node, Tag, Template
from mwparserfromhell.wikicode import Wikicode
from pywikibot.bot import ExistingPageBot
from pywikibot import logging

from WikibaseHelper import WikibaseHelper
from pwb_aux import setup_generator


class BestImageTableCompleter(ExistingPageBot):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.matches = []
        self.wb_helper = WikibaseHelper()
    def treat_page(self) -> None:
        logging.info(f"Processing page {self.current_page}")

        wikicode = mwparserfromhell.parse(self.current_page.text)
        tables = wikicode.filter_tags(matches=lambda node: node.tag == 'table')

        print(f"Found {len(tables)} tables")

        for table in tables:
            rows = table.contents.filter_tags(matches=lambda node: node.tag == 'tr')
            for row in rows[1:]:  # Skip the header row
                cells = row.contents.filter_tags(matches=lambda node: node.tag == 'td')
                if len(cells) == 4:
                    self.process_table_row(cells)

        # Dump new wikicode to page
        with open("pueblos_magicos.txt", "w") as f:
            f.write(str(wikicode))

    def get_wikidata_id(self,name):
        # Function to retrieve Wikidata ID from a page name
        print(f"Extracting wikidata id for {name}")
        wd_item = self.wb_helper.get_wikidata_entity_by_wikipedia_article_name(name, "", lang='it')
        if wd_item:
            return wd_item
        else:
            return ""

    def get_state_and_year(self, cells: list[Tag]):
        # State is the third cell
        state = cells[2].contents.strip_code().strip()

        # Year is the fourth cell
        year = cells[3].contents.strip_code().strip()

        print(f"State: {state}, year: {year}")
        return state, year


    def extract_city_name(self, cell: Tag):
        # cell: ||{{marker|nome=[[Zozocolco de Hidalgo]]|lat= |long=}}
        # We need the wikilink in the nome field withouth eventual pipe
        # and without the wikidata id

        content = cell.contents # type: Wikicode
        marker_template = content.filter_templates(matches=lambda node: node.name == 'marker')[0] # type: Template

        wikilink = marker_template.get("nome").value # type: Wikicode
        return wikilink.filter_wikilinks()[0].title

    def process_table_row(self,cells: list[Tag]):
        #for cell in cells:
        name = self.extract_city_name(cells[1])
        wikidata_id = self.get_wikidata_id(name)

        if not wikidata_id:
            # Prompt the user to enter the wikidata id
            wikidata_id = input(f"Enter wikidata id for {name}: ")

        image = Template("getBestImage")
        image.add("1", wikidata_id)
        image.add("2", "300px")

        marker_template = cells[1].contents.filter_templates(matches=lambda node: node.name == 'marker')[0]
        marker_template.add("wikidata", wikidata_id)

        coords = self.wb_helper.get_lat_long(wikidata_id)
        marker_template.add("lat", coords[0])
        marker_template.add("long", coords[1])

        cells[0].contents = [image]
        cells[1].contents = [marker_template]


def main():
    local_args = pywikibot.handle_args()
    generator, options = setup_generator(local_args)
    bot = BestImageTableCompleter(generator=generator, **options)
    bot.run()

if __name__ == '__main__':
    main()
