from typing import Any, Iterable

import mwparserfromhell
import pywikibot
import logging
from pywikibot.bot import ExistingPageBot
from WikibaseHelper import WikibaseHelper
from pwb_aux import setup_generator

# --- it.wikivoyage specific constants ---
SOURCE_CATEGORY = "Quickbar con codice mappa diverso da Wikidata"
QUICKBAR_TEMPLATE_NAME = "QuickbarCity\n"
QUICKBAR_MAP_PARAM = "Map"
QUICKBAR_LAT_PARAM = "Lat"


class MapCodeQuickbarUpdater(ExistingPageBot):

    def __init__(self, custom_opts, **kwargs):
        super().__init__(**kwargs)
        self.wikibase_helper = WikibaseHelper()
        self.matched_pages = []
        try:
            self.old_code = custom_opts.get("oldcode", "uk")
        except:
            raise ValueError("Invalid custom options")

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
            "summary": f"Fix codice mappa (allineo con wikidata)",
            "watch": "nochange",
            "minor": True,
            "bot": True
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
            return

    def process_templates(self, templates):
        """
        Processes templates to update the data and add additional information.

        :param templates: List of templates to process.
        :type templates: list
        :return: None
        """
        for template in templates:
            # Conditions
            is_target_template = template.name == QUICKBAR_TEMPLATE_NAME
            has_old_value = template.has(QUICKBAR_MAP_PARAM) and template.get(
                QUICKBAR_MAP_PARAM).value.strip().lower() == self.old_code.strip().lower()


            if is_target_template and has_old_value:
                self.matched_pages.append(self.current_page.title())
                wikidata_id = self.current_page.data_item()
                iso_code = self.wikibase_helper.get_iso_3166_1_from_city(wikidata_id)

                if iso_code is not None:
                    template.add(QUICKBAR_MAP_PARAM, iso_code.upper(), before=QUICKBAR_LAT_PARAM, preserve_spacing=True)
                    logging.info(f"Updated template {QUICKBAR_TEMPLATE_NAME} on page {self.current_page.title()}")
            else:
                continue

    def teardown(self) -> None:
        """
        Print the list of pages that were matched and updated.
        :return: None
        """
        pywikibot.output(f"Found {len(self.matched_pages)} pages that were updated:")
        for page in self.matched_pages:
            pywikibot.output(f"\t{page}")

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


def set_custom_opts(args: list[str]) -> dict[str, str]:
    """
    Set custom options for the given arguments.
    In particular following options are supported (i.e. read from command line):

    -addcat:<category_name> - Adds the given category to the pages with empty section.
    -section:<section_name> - The name of the section to check for emptiness.
    -action:<action_name> - The action to perform. Possible values are "dump" and "addcat".

    :param args: List of command line arguments.
    :return: Dictionary of custom options.

    """
    custom_opts = dict()

    if any(arg.startswith("-oldcode") for arg in args):
        custom_opts["oldcode"] = args[[arg.startswith("-oldcode") for arg in args].index(True)].split(":")[1]

    return custom_opts


def main():
    local_args = prepare_generator_args()
    generator, options = setup_generator(local_args)
    custom_opts = set_custom_opts(local_args)
    bot = MapCodeQuickbarUpdater(generator=generator, custom_opts=custom_opts, **options)
    bot.run()


if __name__ == '__main__':
    main()
