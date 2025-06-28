import datetime
from typing import Any

import mwparserfromhell
import pywikibot
from mwparserfromhell.nodes import Template
from mwparserfromhell.wikicode import Wikicode
from pywikibot.bot import ExistingPageBot
from pywikibot import logging

from voy_aux import ArticleTypeCategories, ArticleTypes, ArticleTypeLookup
from pwb_aux import setup_generator
from WikibaseHelper import WikibaseHelper

DEFAULT_SOURCE_CATEGORY = ArticleTypeCategories.REGION.value
DYNAMIC_MAP_TEMPLATE = "MappaDinamica"
REGION_LIST_TEMPLATE = "Regionlist"
WIKIDATA_SUBPARTS_PROP = "P527"
STANDARD_TEMPLATE_COLOR = "StdColor"


class MissingDynamicMapFinder(ExistingPageBot):
    """
    IMPORTANT: DO NOT RUN AUTOMATICALLY -- STILL WORK IN PROGRESS
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.found_matches = []
        self.no_region_list = []
        self.wikibase_helper = WikibaseHelper()
        self.target_section = None
        self.current_article_type = None

    @property
    def edit_opts(self):
        return {
            "summary": "Aggiungo mappa dinamica (auto)",
            "watch": "nochange",
            "minor": True,
            "bot": True
        }

    def init_page(self, item: Any) -> 'pywikibot.page.BasePage':
        """
        Initialize the page to be treated.
        :param item: The item to be treated.
        :return: The page to be treated.
        """
        page = super().init_page(item)
        self.current_article_type = ArticleTypeLookup.get_article_type(page)
        self.set_target_section()
        return page

    def set_target_section(self):
        if self.current_article_type == ArticleTypes.CITY:
            self.target_section = "Come orientarsi"
        elif self.current_article_type == ArticleTypes.REGION:
            self.target_section = "Territori e mete turistiche"
        else:
            raise ValueError(f"Unexpected article type {self.current_article_type}")

    def treat_page(self):
        templates = self.current_page.templatesWithParams()
        has_dynamic_map = any(template[0].title(with_ns=False) == DYNAMIC_MAP_TEMPLATE for template in templates)
        has_regionlist = any(template[0].title(with_ns=False) == REGION_LIST_TEMPLATE for template in templates)

        if not has_dynamic_map and not has_regionlist:
            self.found_matches.append(self.current_page.title())
            subregions = self.wikibase_helper.get_p_values(self.current_page.data_item(), WIKIDATA_SUBPARTS_PROP)
            if not subregions:
                logging.info(f"Page {self.current_page.title()} has no subregions")
                return
            self.found_matches.append(self.current_page.title())
            self._complete_article(subregions)
        elif has_dynamic_map and not has_regionlist:
            self.no_region_list.append(self.current_page.title())
            logging.info(f"Page {self.current_page.title()} has no region list but has dynamic map")

    def _create_shape_template(self, territories: list[str]):

        templates = []
        for i, territory in enumerate(territories):
            template = mwparserfromhell.nodes.Template("Mapshape")
            template.add("type", "geoshape")
            template.add("wikidata", territory)

            color_template = mwparserfromhell.nodes.Template(STANDARD_TEMPLATE_COLOR)
            color_template.add(1, f"T{i + 1}", showkey=False)

            template.add("fill", color_template)
            templates.append(template)

        return templates

    def _get_zoom(self) -> int | str:
        if self.current_article_type == ArticleTypes.CITY:
            return 12
        elif self.current_article_type == ArticleTypes.REGION:
            return 7
        elif self.current_article_type == ArticleTypes.COUNTRY:
            return 5
        elif self.current_article_type == ArticleTypes.DISTRICT:
            return 10
        elif self.current_article_type == ArticleTypes.PARK:
            return 10
        elif self.current_article_type == ArticleTypes.ARCHEOLOGICAL_SITE:
            return 10

        return "auto"

    def _complete_article(self, subregions_list: list[str]):
        """
        Add the dynamic map template to the page, at the beginning of the "Come orientarsi" section,
        before any other text in this section.
        taking the wikidata coordinates from the page
        and setting a default value for zoom dependent on the type of article.
        Width and height are set to 450px as per documentation and it.voy standard.
        :return:
        """
        wikicode = mwparserfromhell.parse(self.current_page.text)
        sections = wikicode.get_sections(flat=False, include_lead=False)

        # find the section "Come orientarsi"
        for section in sections:  # type: Wikicode
            if section.startswith(f"== {self.target_section} =="):
                dyn_map = self._insert_dynamic_map(section)
                shapes_templates = self._insert_mapshapes(section, subregions_list, dyn_map)
                self._insert_region_list(section, subregions_list, shapes_templates)
                break

        if self.current_page.text != str(wikicode):
            pywikibot.showDiff(self.current_page.text, str(wikicode))
            logging.info(f"SECTION:\n {section}")
            self.user_confirm("Do you want to save these changes?")

            # if prompt:
            #     self.current_page.text = str(wikicode)
            #     self.current_page.save(**self.edit_opts)

    def _insert_region_list(self, section: Wikicode, subregions_list: list[str], shapes_templates: list[Template]):

        template = mwparserfromhell.nodes.Template(REGION_LIST_TEMPLATE + "\n")

        for i, subregion in enumerate(subregions_list):
            wikidata_item = pywikibot.ItemPage(self.current_page.site.data_repository(), subregion)
            label = wikidata_item.labels["it"] if "it" in wikidata_item.labels else wikidata_item.labels["en"]

            color_template = mwparserfromhell.nodes.Template(STANDARD_TEMPLATE_COLOR)
            color_template.add(1, f"T{i+1}",showkey=False)

            template.add(f" region{i+1}name", label + "\n", preserve_spacing=True)
            template.add(f" region{i+1}color", color_template,preserve_spacing=True)
            template.add(f" region{i+1}description", "\n\n", preserve_spacing=True)

        section.insert_after(shapes_templates[-1], template)
        section.insert_after(shapes_templates[-1], "\n\n")

    def _insert_mapshapes(self, section: Wikicode, subregions_list: list[str], dyn_map: Template):
        templates = self._create_shape_template(subregions_list)

        for template in templates:
            section.insert_after(dyn_map, template)
        section.insert_after(dyn_map, "\n")
        return templates

    def _insert_dynamic_map(self, section):
        template = self._create_dynamic_map_template()
        heading = section.nodes[0]
        section.insert_after(heading, template)
        section.insert_after(heading, "\n")
        return template

    def _create_dynamic_map_template(self):
        lat, lon = (self.current_page.coordinates()[0].lat, self.current_page.coordinates()[0].lon)
        zoom = self._get_zoom()

        template = mwparserfromhell.nodes.Template(DYNAMIC_MAP_TEMPLATE + "\n")  # type: Template
        template.add(" Lat", " " + str(lat) + "\n")
        template.add("Long", " " + str(lon))
        template.add(" h", " 450 ", preserve_spacing=False)
        template.add(" w", " 450 ", preserve_spacing=False)
        template.add("z", str(zoom) + " \n")
        template.add("view", "Kartographer\n")

        return template

    def teardown(self) -> None:
        self.dump_findings()
        self.log_missing_region_list()

    def dump_findings(self):
        logging.info(f"Found {len(self.found_matches)} matches")
        with open(f"logs/missing_dynamic_map.txt", "w") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for match in self.found_matches:
                f.write(f"* [[{match}]] <small>(check eseguito il {timestamp})</small>\n")

    def log_missing_region_list(self):
        logging.info(f"Found {len(self.no_region_list)} matches")
        with open(f"logs/missing_region_list.txt", "w") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for match in self.no_region_list:
                f.write(f"* [[{match}]] <small>(check eseguito il {timestamp})</small>\n")


def handle_opts() -> list[str]:
    """
    Handles the command line options for the program
    setting the default category and activating the log.

    :return: A list of command line arguments.
    """
    args = pywikibot.handle_args()

    # set default cat, from which articles will be loaded
    if not any(arg.startswith("-cat") for arg in args):
        args.append(f"-catr:{DEFAULT_SOURCE_CATEGORY}")

    return args


def main():
    local_args = handle_opts()
    generator, options = setup_generator(local_args)
    bot = MissingDynamicMapFinder(generator=generator, **options)
    bot.run()


if __name__ == '__main__':
    main()
