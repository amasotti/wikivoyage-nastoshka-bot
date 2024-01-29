import re
from typing import Any

import mwparserfromhell
import pywikibot
from mwparserfromhell.nodes import Template, Node
from mwparserfromhell.wikicode import Wikicode
from pywikibot import textlib, cosmetic_changes
from pywikibot.bot import ExistingPageBot
from wikitextparser import ExternalLink

from WikibaseHelper import WikibaseHelper
from voy_aux import format_template_params, terminate_before_section_level_two
from pwb_aux import setup_generator

# --- it.wikivoyage specific constants ---
SOURCE_CATEGORY = "Tematica Aeroporto"
QUICKBAR_TEMPLATE_NAME = "QuickbarAirport\n"
SECTIONS_WITH_LISTINGS = [
    "Da sapere",
    "Voli",
    "Come arrivare",
    "Come spostarsi",
    "Cosa fare",
    "Acquisti",
    "Dove mangiare",
    "Dove alloggiare",
    "Come restare in contatto",
    "Nei dintorni",
]


class AirportModelApplier(ExistingPageBot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wikibase_helper = WikibaseHelper()
        self.matched_pages = []
        self.wikibase_item = None  # type: pywikibot.ItemPage | None

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
            "summary": f"Applico quickbar e Quickfooter aeroporto",
            "watch": "nochange",
            "minor": False,
            "botflag": True
        }

    def init_page(self, item: Any) -> 'pywikibot.page.BasePage':
        """
        Initialize the page to work on.
        :param item: The page to work on.
        :return: The page to work on.
        """
        page = super().init_page(item)
        self.wikibase_item = page.data_item()  # type: pywikibot.ItemPage
        return page

    def treat_page(self):

        # Skip plurals
        if "aeroporti" in self.current_page.title().lower():
            return

        # Get and parse the page wikicode
        content = self.current_page.text
        wikicode: Wikicode = mwparserfromhell.parse(content)

        # Extract the templates from the page
        templates = wikicode.filter_templates()  # type: list[Template]

        if self.has_right_quickbar_and_quickfooter(templates):
            return

        # delete pagebanner if exists
        banner, wikicode = self.remove_pagebanner(wikicode)

        # Remove image if same as wikidata image
        image, didascalia, wikicode = self.remove_image(wikicode)

        sito = self.cleanup_intro(wikicode)

        # add quickbar template on the very top of the page
        self.add_quickbar(wikicode, banner, image, didascalia, sito)

        # Add examples of listing to use
        self.add_listing_example(wikicode)

        # with open(f"output/listing_example_{self.current_page.title()}.txt", "w") as p:
        #     p.write(str(wikicode))
        #     p.close()

        # add space separator {{-}} after each main section (level 2)
        #self.clear_space_after_sections(wikicode)

        # with open(f"output/separators_example_{self.current_page.title()}.txt", "w") as p:
        #     p.write(str(wikicode))
        #     p.close()

        self.remove_IATA(wikicode)

        # modify quickfooter on the very bottom of the page
        self.process_quickfooter(wikicode)

        self.matched_pages.append(self.current_page.title())

        wikicode_str = format_template_params(str(wikicode))
        wikicode_str = terminate_before_section_level_two(wikicode_str)

        pywikibot.showDiff(content, wikicode_str)
        with open(f"output/wikitext_{self.current_page.title()}.txt", "w") as p:
            p.write(wikicode_str)
            p.close()

            self.user_confirm("Do you want to save the page?")

    def remove_IATA(self, wikicode: Wikicode):
        # ({{IATA|XXX}}) -> ""
        templates = wikicode.filter_templates()  # type: list[Template]
        for template in templates:
            if template.name.matches("IATA"):
                # remove the template
                wikicode.remove(template)
                wikicode.replace(" ()", "")

    def cleanup_intro(self, wikicode: Wikicode):
        # Identify the bold external link and replace it with just the text, without the link
        initial_section = wikicode.get_sections()[0]  # type: Node
        external_links = initial_section.filter_external_links()
        for link in external_links:  # type: ExternalLink
            try:
                if link.title.strip().lower() == self.current_page.title().lower():
                    wikicode.replace(link, self.current_page.title(with_ns=False,underscore=False))
                    return link.url.strip()
            except Exception as e:
                print(e)
                print(link)
                print(link.title)
                return ""

    def has_right_quickbar_and_quickfooter(self, templates: list[Template]) -> bool:
        for template in templates:
            if template.name.matches(QUICKBAR_TEMPLATE_NAME):
                pywikibot.output(f"Already has right quickbar: {self.current_page.title()}")
                return True
            if template.name.matches("Quickfooter"):
                # if the first argument is "Aeroporto", then it's the right template
                if template.params[0].value.strip() == "Aeroporto":
                    pywikibot.output(f"Already has right quickfooter: {self.current_page.title()}")
                    return True
        return False

    def remove_pagebanner(self, wikicode: Wikicode) -> (str, Wikicode):
        templates = wikicode.filter_templates()  # type: list[Template]
        for template in templates:
            if template.name.matches("pagebanner"):
                wikicode.remove(template)
                pywikibot.output(f"Removed pagebanner from {self.current_page.title()}")
                if template.has(1):
                    banner_image = template.get(1).value.strip()
                    return banner_image, wikicode
                break
        return '', wikicode

    def remove_image(self, wikicode: Wikicode) -> (str, str, Wikicode):
        # Search for a File wikilink that matches the wikidata image
        try:
            # voy_image is the first image in the wikicode
            wikilinks = wikicode.filter_wikilinks()
            for wikilink in wikilinks:  # type: Wikicode
                if "File:" in wikilink.title:
                    voy_image = wikilink.title.strip().replace("File:", "")
                    voy_description = wikilink.text.strip().replace("|", "").replace("thumb", "").replace("right",
                                                                                                          "").replace(
                        "left", "")
                    voy_description = voy_description.replace("miniatura", "").replace("destra", "").replace("sinistra",
                                                                                                             "")
                    wikicode.remove(wikilink)
                    pywikibot.output(f"Found image {voy_image} in {self.current_page.title()}")
                    return voy_image, voy_description, wikicode
            return "", "", wikicode
        except Exception as e:
            pywikibot.output(f"Error while removing image from {self.current_page.title()}: {e}")
            return "", "", wikicode

    def format_param_value(self, value: str):
        # replace leading and trailing spaces with no space, no matter how many
        cleaned = str(value).strip()
        cleaned = cleaned.strip().replace("\n", "").replace(" ", " ")
        # Add one space before and a new line after
        return " " + cleaned + "\n"

    def add_quickbar(self, wikicode: Wikicode, banner: str, image: str, didascalia: str, sito: str):
        # Add the quickbar template
        quickbar_template = Template(QUICKBAR_TEMPLATE_NAME)

        quickbar_template.add("Nome ufficiale ", self.format_param_value("<!--Nome dell'aeroporto-->"),
                              preserve_spacing=True)

        # Banner
        banner = banner if banner else "<!--Nome file dell'immagine.jpg-->"
        quickbar_template.add("Banner ", self.format_param_value(banner), preserve_spacing=False)

        # DidascaliaBanner
        quickbar_template.add("DidascaliaBanner ", self.format_param_value("<!--Didascalia del banner-->"),
                              preserve_spacing=False)

        # Immagine
        image = image if image else "<!--Nome file dell'immagine.jpg-->"
        quickbar_template.add("Immagine ", self.format_param_value(image), preserve_spacing=False)

        # Didascalia
        didascalia = didascalia if didascalia else "<!--Didascalia dell'immagine-->"
        quickbar_template.add("Didascalia ", self.format_param_value(didascalia), preserve_spacing=False)

        # Stato
        try:
            stato = self.wikibase_item.get()["claims"]["P17"][0].getTarget().labels["it"]
        except:
            stato = "<!--[[Nome dello stato di appartenenza]]-->"
        quickbar_template.add("Stato", " [[" + stato + "]]\n", preserve_spacing=False)

        # Stato federato
        quickbar_template.add("Stato federato ",
                              self.format_param_value("<!--[[Nome dello stato federato di appartenenza]]-->"),
                              preserve_spacing=False)

        # Regione
        quickbar_template.add("Regione ", self.format_param_value("<!--[[Nome della regione di appartenenza]]-->"),
                              preserve_spacing=False)

        # Territorio
        quickbar_template.add("Territorio ", self.format_param_value("<!--[[Nome del territorio di appartenenza]]-->"),
                              preserve_spacing=False)

        # Città
        quickbar_template.add("Città ", self.format_param_value("<!--[[Nome della città in cui è situato]]-->"),
                              preserve_spacing=False)

        # Sito ufficiale
        sito = sito if sito else "<!--https://-->"
        quickbar_template.add("Sito ufficiale ", self.format_param_value(sito), preserve_spacing=False)

        # Map
        try:
            codice_iso = self.wikibase_helper.get_iso_3166_1_from_city(self.wikibase_item).lower()
        except:
            codice_iso = "<!--tld (sigla a due lettere senza il punto) dello Stato di appartenenza-->"
        quickbar_template.add("Map ", self.format_param_value(codice_iso), preserve_spacing=False)

        coords = self.wikibase_helper.get_lat_long(self.wikibase_item.title())

        # Lat
        quickbar_template.add("Lat ", coords[0] + "\n", preserve_spacing=False)

        # Long
        quickbar_template.add("Long ", coords[1] + "\n", preserve_spacing=False)

        wikicode.insert(0, quickbar_template)
        pywikibot.output(f"Added quickbar to {self.current_page.title()}")

    def add_space_end_of_section(self, wikicode: Wikicode, sec_name):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            try:
                if sec.nodes[0].title.strip() == sec_name:
                    space_template = Template("-")
                    sec.insert_after(sec.nodes[-1], space_template)
                    sec.insert_after(sec.nodes[-1], "\n")
            except Exception as e:
                continue

    def clear_space_after_sections(self, wikicode: Wikicode):
        for sec in SECTIONS_WITH_LISTINGS:
            self.add_space_end_of_section(wikicode, sec)
        pywikibot.output(f"Processed space separator to {self.current_page.title()}")

    def add_do_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Cosa fare":
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{do\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| orari= | prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_buy_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Acquisti":
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{buy\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| orari= | prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_eat_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Dove mangiare":
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{eat\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| | orari= | prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_sleep_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Dove alloggiare":
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{sleep\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| checkin= | checkout=| prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_listing_example(self, wikicode: Wikicode):
        try:
            self.add_do_listing_example(wikicode)
            self.add_buy_listing_example(wikicode)
            self.add_eat_listing_example(wikicode)
            self.add_sleep_listing_example(wikicode)
        except Exception as e:
            pywikibot.output(f"Error while adding listing example to {self.current_page.title()}: {e}")

    def process_quickfooter(self, wikicode: Wikicode):
        quickfooter_templates = wikicode.filter_templates(matches=lambda template: template.name.matches("Quickfooter"))
        if len(quickfooter_templates) == 0:
            pywikibot.output(f"Quickfooter not found in {self.current_page.title()}")
        else:
            quickfooter = quickfooter_templates[0]  # type: Template
            quickfooter.params[0].value = "Aeroporto\n"
            if quickfooter.has("Tema"):
                quickfooter.remove("Tema")

    def teardown(self) -> None:
        """
        Print the list of pages that were matched and updated.
        :return: None
        """
        pywikibot.output(f"Found {len(self.matched_pages)} pages that were updated:")
        with open("logs/airport_model_applier.log", "a") as f:
            f.write("Found {len(self.matched_pages)} pages that were updated:\n")
            for page in self.matched_pages:
                f.write(f"* {page} \n")


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
    #    custom_opts = set_custom_opts(local_args)
    bot = AirportModelApplier(generator=generator, **options)
    bot.run()


if __name__ == '__main__':
    main()
