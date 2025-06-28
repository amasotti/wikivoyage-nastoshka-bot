import mwparserfromhell
import pywikibot
from pywikibot import logging
from pywikibot.bot import ExistingPageBot

# LOCAL IMPORTS
from WikibaseHelper import WikibaseHelper
from pwb_aux import setup_generator

SOURCE_CATEGORY = "Mappa dinamica senza coordinate"
DYNAMIC_MAP_TEMPLATE = "MappaDinamica\n"  # Peculiar case
DYNAMIC_MAP_LAT_PARAM = "Lat"
DYNAMIC_MAP_LON_PARAM = "Long"
DYNAMIC_MAP_ZOOM_PARAM = "z"
DYNAMIC_MAP_HEIGHT_PARAM = "h"
DYNAMIC_MAP_WIDTH_PARAM = "w"


class DynamicMapFiller(ExistingPageBot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wd_helper = WikibaseHelper()
        self.matches = []

    def treat_page(self) -> None:
        logging.info(f"Processing page {self.current_page}")

        self.matches.append(self.current_page.title())
        content = self.current_page.text
        wikicode = mwparserfromhell.parse(content)

        templates = wikicode.filter_templates()
        self._process_dynamic_map(templates)

        content = str(wikicode)
        if content != self.current_page.text:
            pywikibot.showDiff(content, self.current_page.text)
            self.current_page.text = content
            self.current_page.save(summary="Aggiungo le coordinate alla mappa dinamica",
                                   watch='nochange',
                                   minor=True,
                                   )

    def teardown(self) -> None:
        logging.info(f"Found {len(self.matches)} matches")
        with open("dynamic_map_matches.txt", "w") as f:
            f.write(f"Found {len(self.matches)} matches\n")
            for match in self.matches:
                f.write(f"* [[{match}]]\n")

    def _process_dynamic_map(self, templates) -> None:
        """
        Add wikidata ids to the citylist templates if they are missing and can be found, updating the
        templates in place
        :param templates:
        :return:
        """
        for template in templates:
            # Conditions (We iterate a category that is supposed to contain only dynamic maps without coordinates)
            if template.name == DYNAMIC_MAP_TEMPLATE:
                wikidata_id = self.current_page.data_item()
                logging.info(f"Found wikidata item for {self.current_page}: {wikidata_id.title()}")

                coords = self.wd_helper.get_lat_long(wikidata_id.title())

                if coords[0] is None:
                    logging.warning(f"\tCould not find coordinates for {self.current_page} -- keeping empty")
                else:
                    logging.info(f"\tFound coordinates for {self.current_page}: {coords}")
                    template.add(DYNAMIC_MAP_LAT_PARAM, str(" " + coords[0]), before=DYNAMIC_MAP_HEIGHT_PARAM,
                                 preserve_spacing=True)
                    template.add(DYNAMIC_MAP_LON_PARAM, str(" " + coords[1]), before=DYNAMIC_MAP_HEIGHT_PARAM,
                                 preserve_spacing=True)

                    # More or less an informed guess, needs to be checked
                    if self.is_in_at_least_one_cat(["Città"]):
                        template.add(DYNAMIC_MAP_ZOOM_PARAM, "12", preserve_spacing=True)
                    elif self.is_in_at_least_one_cat(["Regione"]):
                        template.add(DYNAMIC_MAP_ZOOM_PARAM, "6", preserve_spacing=True)
                    elif self.is_in_at_least_one_cat(["Distretto"]):
                        template.add(DYNAMIC_MAP_ZOOM_PARAM, "10", preserve_spacing=True)
                    elif self.is_in_at_least_one_cat(["Parco", "Sito archeologico"]):
                        template.add(DYNAMIC_MAP_ZOOM_PARAM, "10", preserve_spacing=True)

        return templates

    def is_in_at_least_one_cat(self, category: list[str]) -> bool:

        cat_fullnames = [f"Categoria:{cat}" for cat in category]

        # Check at least one category is present
        return any(cat in self.current_page.categories() for cat in cat_fullnames)


def prepare_generator_args() -> list[str]:
    """
    Handles the command line options for the program.
    The args are then passed to the generator

    :return: A list of command line arguments.
    """
    args = pywikibot.handle_args()

    # set default cat
    if not any(arg.startswith("-cat") for arg in args):
        args.append(f"-catr:{SOURCE_CATEGORY}")

    return args


def main():
    local_args = prepare_generator_args()
    generator, options = setup_generator(local_args)
    bot = DynamicMapFiller(generator=generator, **options)
    bot.run()


if __name__ == '__main__':
    main()
