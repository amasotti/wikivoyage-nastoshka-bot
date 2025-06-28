import re
from typing import Any

import mwparserfromhell
import pywikibot
from pywikibot import logging
from mwparserfromhell.nodes import Template, Node
from mwparserfromhell.wikicode import Wikicode
from pywikibot.bot import ExistingPageBot
from wikitextparser import ExternalLink

from WikibaseHelper import WikibaseHelper
from voy_aux import format_template_params, terminate_before_section_level_two, format_section_titles, add_quickbar_image, add_banner_image, add_mappa_dinamica
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
    "Informazioni utili"
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
                 - "bot": A boolean indicating whether the edit should be flagged as a bot edit (default: True).
        """
        return {
            "summary": f"Applico modello [[Wikivoyage:Modello aeroporto]]",
            "watch": "nochange",
            "minor": False,
            "bot": True
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

        self.check_sections(wikicode)

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
        #self.add_listing_example(wikicode)

        # remove IATA template
        self.remove_IATA(wikicode)

        # modify quickfooter on the very bottom of the page
        self.process_quickfooter(wikicode)

        # Add dynamic map
        self.add_dynamic_map(wikicode)

        wikicode_str = format_template_params(str(wikicode))
        wikicode_str = terminate_before_section_level_two(wikicode_str)
        #wikicode_str = format_section_begin(wikicode_str)
        wikicode_str = format_section_titles(wikicode_str)

        # Save the page
        self.matched_pages.append(self.current_page.title())

        pywikibot.showDiff(content, wikicode_str)
        with open(f"output/wikitext_{self.current_page.title()}.txt", "w") as p:
            p.write(wikicode_str)
            p.close()

            shall_be_saved = self.user_confirm("Do you want to save the page?")
            if shall_be_saved:
                self.current_page.text = wikicode_str
                self.current_page.save(**self.edit_opts)


    def remove_IATA(self, wikicode: Wikicode):
        # ({{IATA|XXX}}) -> ""
        templates = wikicode.filter_templates()  # type: list[Template]
        for template in templates:
            if template.name.matches("IATA"):
                # remove the template
                wikicode.remove(template)
                wikicode.replace(" ()", "")
                break # only one IATA template is allowed

    def cleanup_intro(self, wikicode: Wikicode):
        # Identify the bold external link and replace it with just the text, without the link
        initial_section = wikicode.get_sections()[0]  # type: Node
        wikicode.replace("L''''", "'''")
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

    def check_sections(self, wikicode: Wikicode):
        # It should have the right sections, in the right order
        sections = wikicode.get_sections(levels=[2])
        # if len(sections) < 11:
        #     raise Exception(f"Found {len(sections)} sections, expected 12")

        for sec in sections: # type: Wikicode
            if sec.nodes[0].title.strip() not in SECTIONS_WITH_LISTINGS:
                logging.error(f"Wrong section: {sec.nodes[0].title.strip()}")

            # Check subsections
            if sec.nodes[0].title.strip() == "Come arrivare":
                # Check that ["In auto", "Parcheggi", "In treno", "In autobus"] are present
                due_sections = ["In auto", "In treno", "In autobus"]
                for subsec in due_sections:
                    if subsec not in str(sec):
                        logging.error(f"Missing subsection: {subsec}")

            elif sec.nodes[0].title.strip() == "Informazioni utili":
                due_sections = ["=== Noleggio auto ===", "=== Trasferimenti privati ==="]
                for subsec in due_sections:
                    if subsec not in str(sec):
                        sec.insert_after(sec.nodes[1],f"<!--{subsec}-->\n" +
                                   """<!--* {{listing
| nome= | alt= | sito= | email=
| indirizzo= | lat= | long= | indicazioni=
| tel= | numero verde= | fax=
| orari= | prezzo=
| descrizione=
}}-->\n
""")

            # Some airports have "Sicurezza" as a subsection, that's not in the model
            if "== Sicurezza ==\n" in str(wikicode):
                logging.error(f"Found Sicurezza section in {self.current_page.title()}")




        # Check if the sections are in the right order


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
        banner = banner if banner else self.wikibase_helper.get_banner(self.wikibase_item).replace("File:", "")
        if not banner:
            banner = "<!--Nome file dell'immagine.jpg-->"
        quickbar_template.add("Banner ", self.format_param_value(banner), preserve_spacing=False)

        # DidascaliaBanner
        quickbar_template.add("DidascaliaBanner ", self.format_param_value("<!--Didascalia del banner-->"),
                              preserve_spacing=False)

        # Immagine
        image = image if image else self.wikibase_helper.get_image(self.wikibase_item).replace("File:", "")
        if not image:
            image = "<!--Nome file dell'immagine.jpg-->"
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
        wikidata_citta = self.wikibase_helper.get_administrative_unit(self.wikibase_item)
        if wikidata_citta:
            citta = "[[" + wikidata_citta + "]]"
        else:
            citta = "<!--[[Nome della città in cui è situato]]-->"
        quickbar_template.add("Città ", self.format_param_value(citta), preserve_spacing=False)

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

    def add_dynamic_map(self, wikicode: Wikicode):
        templates = wikicode.filter_templates()  # type: list[Template]
        for template in templates:
            if template.name.matches("MappaDinamica\n"):
                return

        sections = wikicode.get_sections(levels=[2])
        for sec in sections:
            if sec.nodes[0].title.strip() == "Come arrivare":
                coords = self.wikibase_helper.get_coords(self.wikibase_item)
                mappa = Template("MappaDinamica\n")
                mappa.add("Lat", coords["lat"] + "\n", preserve_spacing=False)
                mappa.add("Long", coords["long"] + "\n", preserve_spacing=False)
                mappa.add("h", "450", preserve_spacing=False)
                mappa.add("w", "450", preserve_spacing=False)
                mappa.add("z", "14\n", preserve_spacing=False)
                sec.insert_after(sec.nodes[1], mappa)

    def has_listing(self, wikicode: Wikicode, listing_type: str) -> bool:
        templates = wikicode.filter_templates()
        for template in templates:
            if template.name.matches(listing_type):
                return True
        return False

    def add_do_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Cosa fare":
                if self.has_listing(wikicode, "do"):
                    return
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{do\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| orari= | prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_buy_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Acquisti":
                if self.has_listing(wikicode, "buy"):
                    return
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{buy\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| orari= | prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_eat_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Dove mangiare":
                if self.has_listing(wikicode, "eat"):
                    return
                sec.insert_after(sec.nodes[0],
                                 """\n<!--* {{eat\n| nome= | alt= | sito= | email=\n| indirizzo= | lat= | long= | indicazioni=\n| tel= | numero verde= | fax=\n| | orari= | prezzo=\n| descrizione=\n}}-->\n""")
                break

    def add_sleep_listing_example(self, wikicode: Wikicode):
        secs = wikicode.get_sections(levels=[2])
        for sec in secs:
            if sec.nodes[0].title.strip() == "Dove alloggiare":
                if self.has_listing(wikicode, "sleep"):
                    return
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
