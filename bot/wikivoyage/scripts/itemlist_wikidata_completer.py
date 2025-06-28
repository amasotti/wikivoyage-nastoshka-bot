from typing import Any, Iterable

import mwparserfromhell
import pywikibot
from mwparserfromhell.nodes import Template
from mwparserfromhell.wikicode import Wikicode
from pywikibot import logging
from pywikibot.bot import ExistingPageBot
from WikibaseHelper import WikibaseHelper
from pwb_aux import setup_generator
from voy_aux import (
    format_template_params,
    terminate_before_section_level_two,
    add_quickbar_image,
    add_banner_image,
    add_mappa_dinamica,
)

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

    def __init__(self, custom_opts, **kwargs):
        super().__init__(**kwargs)
        self.wikibase_helper = WikibaseHelper()
        self.interactive = custom_opts.get("interactive", False)

    @property
    def edit_opts(self):
        """
        :return: A dictionary containing options for editing.
                 The dictionary has the following keys:
                 - "summary": A string representing the summary for the edit.
                 - "watch": A string indicating whether to watch the page for changes.
                            Possible values are "watch", "unwatch" (default: "nochange").
                 - "minor": A boolean indicating whether the edit should be marked as minor (default: True).
                 - "bot": A boolean indicating whether the edit should be flagged as a bot edit (default: True).
        """
        return {
            "summary": f"Completo itemlists con codici wikidata",
            "watch": "nochange",
            "minor": False,
            "bot": True,
        }

    def get_current_page_url(self):
        """
        Returns the current page URL in the format "https://{lang}.{family}.org/wiki/{title}".

        :return: The URL of the current page
        """
        lang = self.current_page.site.lang
        family = self.current_page.site.family
        title = self.current_page.title()

        return f"https://{lang}.{family}.org/wiki/{title}"

    def treat_page(self):
        """
        Processes a page by extracting templates, adding wikidata ids and saving the page.

        :return: None
        """
        # Get and parse the page wikicode
        content = self.current_page.text
        wikicode = mwparserfromhell.parse(content)

        # Extract the templates from the page
        templates = wikicode.filter_templates()

        # Add wikidata ids to the templates if they are missing and can be found
        self.process_templates(templates)

        # Add quickbar image and banner image
        self._process_quickbar(templates)

        # Add mappa dinamica
        self._process_map(wikicode, templates)

        # Format the page
        wikicode_str = str(wikicode)
        wikicode_str = format_template_params(wikicode_str)
        # wikicode_str = terminate_before_section_level_two(wikicode_str)

        self._apply_changes(wikicode_str)

    def _apply_changes(self, content):
        """
        Applies the changes to the page if the user accepts them.
        :param content: str, the new content of the page
        :return: None
        """
        if content != self.current_page.text:
            pywikibot.showDiff(self.current_page.text, content)
            prompt = self.user_confirm(
                f"Do you want to accept these changes for {self.get_current_page_url()}?"
            )
            if prompt:
                self.current_page.text = content
                self.current_page.save(**self.edit_opts)

    def process_templates(self, templates: Iterable[Template]) -> None:
        """
        Processes templates to update the data and add additional information.

        :param templates: List of templates to process.
        :type templates: list
        :return: None
        """
        for template in templates:
            # Conditions
            conditions_are_met = self._check_conditions(template)

            # Skip other templates and those that already have a wikidata param filled
            if not conditions_are_met:
                continue

            # Get the name and alt label of the item for further processing
            name_label = template.get(NAME_PARAM_NAME).value.strip()
            alt_label = template.get(ALT_PARAM_NAME, "").value.strip()
            wikidata_id = self.try_retrieve_wikidata_id(name_label, alt_label)

            # Wikipedia has a page for the item, use it
            if wikidata_id:
                self.process_param_addition(name_label, template, wikidata_id)
                continue

            # Wikipedia does not have a page for the item, ask the user
            if self.interactive:
                self.process_user_given_wikidata_id(name_label, template)
                continue

            logging.warning(
                f"\tCould not find wikidata item for {name_label} -- keeping empty"
            )

    def try_retrieve_wikidata_id(self, name_label: str, alt_label: str) -> str:

        wikidata_id = (
            self.wikibase_helper.get_wikidata_entity_by_wikipedia_article_name(
                name_label, alt_label
            )
        )

        return wikidata_id if wikidata_id else ""

    def process_user_given_wikidata_id(
        self, name_label: str, template: Template
    ) -> None:
        """
        Processes the wikidata id given by the user. If the id is valid, it is added to the template.
        :param name_label: str, the name of the item
        :param template: the template to update
        :return: None (updates the template in place)
        """
        wikidata_id = self.get_user_input(name_label).strip()
        if wikidata_id.startswith("Q"):
            self.process_param_addition(name_label, template, wikidata_id)

    def process_param_addition(
        self, item_label: str, template: Template, wikidata_id: str
    ) -> None:
        self._process_coordinates(item_label, wikidata_id, template)
        self._process_wikidata(item_label, wikidata_id, template)

    def _check_conditions(self, template: Template) -> bool:
        """
        Checks if the given template satisfies the conditions to be processed.
        Conditions:
        - the template is a target template
        - the template does not have a wikidata param or the wikidata param is empty

        :param template: the template to check
        :return: True if the template satisfies the conditions, False otherwise
        """
        return self._check_target_template(
            template
        ) and self._check_wikidata_param_needs_processing(template)

    def _check_target_template(self, template: Template) -> bool:
        """
        Checks if the given template is a target template
        Target templates in this script are {{Città}} and {{Destinazione}}

        :param template: the template to check
        :return: True if the template is a target template, False otherwise
        """
        return (
            template.name == CITY_TEMPLATE_ITEM_NAME
            or template.name == DESTINATION_TEMPLATE_ITEM_NAME
        )

    def _check_wikidata_param_needs_processing(self, template: Template) -> bool:
        """
        Checks if the given template:
        - does not have a wikidata param
        - has a wikidata param but it is empty

        :param template: the template to check
        :return: True if the template needs processing, False otherwise
        """
        return not template.has(WIKIDATA_PARAM_NAME) or (
            template.has(WIKIDATA_PARAM_NAME)
            and template.get(WIKIDATA_PARAM_NAME).value.strip() == ""
        )

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
            pywikibot.logging.warning(
                f"\tCould not find coordinates for {name} -- keeping empty"
            )
        else:
            pywikibot.logging.info(f"\tFound coordinates for {name}: {coords}")
            template.add(
                LAT_PARAM_NAME,
                coords[0],
                before=DESCRIPTION_PARAM_NAME,
                preserve_spacing=True,
            )
            template.add(
                LON_PARAM_NAME,
                coords[1],
                before=DESCRIPTION_PARAM_NAME,
                preserve_spacing=True,
            )

    def _process_wikidata(self, name, wikidata_id, template: Template):
        """
        Add the wikidata id to the template if it exists. Basically a check that the given wikidata id
        is not an empty string. Also logs the operation
        :param name:
        :param wikidata_id:
        :param template:
        :return:
        """
        if wikidata_id == "":
            pywikibot.logging.error(
                f"\tCould not find wikidata item for {name} -- keeping empty"
            )
        else:
            pywikibot.logging.info(f"\tFound wikidata item for {name}: {wikidata_id}")
            template.add(
                WIKIDATA_PARAM_NAME,
                wikidata_id,
                before=DESCRIPTION_PARAM_NAME,
                preserve_spacing=True,
            )

    def _process_quickbar(self, templates: Iterable[Template]):
        image = self.wikibase_helper.get_image(self.current_page.data_item())
        banner = self.wikibase_helper.get_banner(self.current_page.data_item())
        if image:
            add_quickbar_image(templates, image)
        if banner:
            add_banner_image(templates, banner)

    def _process_map(self, wikicode: Wikicode, templates: Iterable[Template]) -> None:
        coords = self.wikibase_helper.get_coords(self.current_page.data_item())
        add_mappa_dinamica(wikicode, templates, coords, 8)

    def get_user_input(self, item_label):
        """
        Gets user input for the wikidata item id
        :param item_label: str, the label of the item
        :return: str, the wikidata item id
        """
        wikidata_id = input(f"Please enter the wikidata item id for {item_label}: ")
        return wikidata_id


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


def set_custom_opts(local_args):
    custom_opts = dict()

    if any(arg.startswith("-interactive") for arg in local_args):
        custom_opts["interactive"] = True

    return custom_opts


def main():
    local_args = prepare_generator_args()
    generator, options = setup_generator(local_args)
    custom_opts = set_custom_opts(local_args)
    bot = ItemListWikidataCompleter(
        generator=generator, custom_opts=custom_opts, **options
    )
    bot.run()


if __name__ == "__main__":
    main()
