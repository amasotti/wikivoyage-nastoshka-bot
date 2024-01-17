from typing import Any

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import ExistingPageBot
from WikibaseHelper import WikibaseHelper

DESTINATION_TEMPLATE_ITEM_NAME = "Destinazione"
CITY_TEMPLATE_ITEM_NAME = "Città"
TARGET_CATEGORY = "Itemlist_con_errori_di_compilazione"
WIKIDATA_PARAM_NAME = "wikidata"
NAME_PARAM_NAME = "nome"
ALT_PARAM_NAME = "alt"
LAT_PARAM_NAME = "lat"
LON_PARAM_NAME = "long"
DESCRIPTION_PARAM_NAME = "descrizione"

class ItemListWikidataCompleter(ExistingPageBot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wikibase_helper = WikibaseHelper()

    @property
    def edit_opts(self):
        return {
            "summary": f"Completo itemlists con codici wikidata",
            "watch": "nochange",
            "minor": True,
            "botflag": True
        }

    def treat_page(self):
        # Get and parse the page wikicode
        content = self.current_page.text
        wikicode = mwparserfromhell.parse(content)

        # Extract the templates from the page
        templates = wikicode.filter_templates()

        # Add wikidata ids to the templates if they are missing and can be found
        self.process_templates(templates)


        # Save the page
        content = str(wikicode)
        pywikibot.showDiff(content, self.current_page.text)
        self.current_page.text = content
        self.current_page.save(**self.edit_opts)

    def process_templates(self, templates):
        for template in templates:
            # Conditions
            is_target_template = (template.name == CITY_TEMPLATE_ITEM_NAME
                                  or template.name == DESTINATION_TEMPLATE_ITEM_NAME)
            has_not_wikidata = not template.has(WIKIDATA_PARAM_NAME) or (
                        template.has(WIKIDATA_PARAM_NAME) and template.get(WIKIDATA_PARAM_NAME).value.strip() == "")

            if is_target_template and has_not_wikidata:
                name_label = template.get(NAME_PARAM_NAME).value.strip()
                try:
                    alt = template.get(ALT_PARAM_NAME).value.strip()
                except:
                    alt = ""
                wikidata_id = self.wikibase_helper.get_wikidata_entity_by_wikipedia_article_name(name_label, alt,
                                                                                                 lang='it')
                # Try to also add coordinates
                self._process_coordinates(name_label, wikidata_id, template)
                self._process_wikidata(name_label, wikidata_id, template)

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

        coords = self.wikibase_helper.get_lat_long(wikidata_id)
        if coords[0] is None:
            pywikibot.logging.warning(f"\tCould not find coordinates for {name} -- keeping empty")
        else:
            pywikibot.logging.info(f"\tFound coordinates for {name}: {coords}")
            template.add(LAT_PARAM_NAME, coords[0], before=DESCRIPTION_PARAM_NAME, preserve_spacing=True)
            template.add(LON_PARAM_NAME, coords[1], before=DESCRIPTION_PARAM_NAME, preserve_spacing=True)

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
            pywikibot.logging.error(f"\tCould not find wikidata item for {name} -- keeping empty")
        else:
            pywikibot.logging.info(f"\tFound wikidata item for {name}: {wikidata_id}")
            template.add(WIKIDATA_PARAM_NAME, wikidata_id, before=DESCRIPTION_PARAM_NAME, preserve_spacing=True)


def handle_opts() -> list[str]:
    args = pywikibot.handle_args()

    # set default cat
    if not any(arg.startswith("-cat") for arg in args):
        args.append(f"-catr:{TARGET_CATEGORY}")

    # activate log
    if not any(arg.startswith("-log") for arg in args):
        args.append("-log")

    return args


def setup_generator(local_args: list[str]) -> tuple[pagegenerators.GeneratorFactory, dict[str, Any]]:
    options = {}
    genFactory = pagegenerators.GeneratorFactory()
    for arg in genFactory.handle_args(local_args):
        if arg.startswith('-'):
            arg, sep, value = arg.partition(':')
            if value != '':
                options[arg[1:]] = value if not value.isdigit() else int(value)
            else:
                options[arg[1:]] = True
    generator = genFactory.getCombinedGenerator()
    return generator, options


def main():
    local_args = handle_opts()
    generator, options = setup_generator(local_args)
    bot = ItemListWikidataCompleter(generator=generator, **options)
    bot.run()

if __name__ == '__main__':
    main()
