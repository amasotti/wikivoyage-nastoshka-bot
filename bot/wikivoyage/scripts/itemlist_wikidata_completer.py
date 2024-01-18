from typing import Any, Iterable

import mwparserfromhell
import pywikibot
from pywikibot.bot import ExistingPageBot
from WikibaseHelper import WikibaseHelper
from pwb_aux import setup_generator

# --- it.wikivoyage specific constants ---
DESTINATION_TEMPLATE_ITEM_NAME = "Destinazione"
CITY_TEMPLATE_ITEM_NAME = "Città"
SOURCE_CATEGORY = "Itemlist_con_errori_di_compilazione"
WIKIDATA_PARAM_NAME = "wikidata"
NAME_PARAM_NAME = "nome"
ALT_PARAM_NAME = "alt"
LAT_PARAM_NAME = "lat"
LON_PARAM_NAME = "long"
DESCRIPTION_PARAM_NAME = "descrizione"


class ItemListWikidataCompleter(ExistingPageBot):
    """
    ``ItemListWikidataCompleter``

    Class that extends ``ExistingPageBot`` and is used to complete itemlists with
    wikidata codes.

    Attributes:
        - ``wikibase_helper``: Instance of class ``WikibaseHelper``.

    Methods:
        - ``__init__``: Constructs a new ``ItemListWikidataCompleter`` object.
        - ``edit_opts``: Returns options for editing the page.
        - ``treat_page``: Processes a page by extracting templates, adding wikidata ids and saving the page.
        - ``process_templates``: Processes templates by checking if they are target templates and adding wikidata ids if missing.
        - ``_process_coordinates``: Adds coordinates to the template if they exist.
        - ``_process_wikidata``: Adds the wikidata id to the template if it exists.

    Example usage:

    ```python
    completer = ItemListWikidataCompleter()
    completer.run()
    ```
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wikibase_helper = WikibaseHelper()

    @property
    def edit_opts(self):
        """
        :return: A dictionary containing options for editing.
                 The dictionary has the following keys:
                 - "summary": A string representing the summary for the edit.
                 - "watch": A string indicating whether to watch the page for changes.
                            Possible values are "watch", "unwatch" (default: "nochange").
                 - "minor": A boolean indicating whether the edit should be marked as minor (default: True).
                 - "botflag": A boolean indicating whether the edit should be flagged as a bot edit (default: True).
        """
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
        if content != self.current_page.text:
            pywikibot.showDiff(content, self.current_page.text)
            self.current_page.text = content
            self.current_page.save(**self.edit_opts)
        else:
            self.skip_page(self.current_page)

    def process_templates(self, templates):
        """
        Processes templates to update the data and add additional information.

        :param templates: List of templates to process.
        :type templates: list
        :return: None
        """
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
    bot = ItemListWikidataCompleter(generator=generator, **options)
    bot.run()


if __name__ == '__main__':
    main()
