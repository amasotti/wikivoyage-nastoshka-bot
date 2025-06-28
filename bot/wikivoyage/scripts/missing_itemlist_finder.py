import datetime
from enum import Enum
import pywikibot
from pywikibot import logging
from pywikibot.bot import ExistingPageBot
from pwb_aux import setup_generator


class AllowedActions(Enum):
    ADD_CAT = "add-cat"
    REMOVE_CAT = "remove-cat"
    ADD_DUMP = "add-dump"
    REMOVE_DUMP = "remove-dump"


SOURCE_CATEGORY = "Regione"  # Very unlikely that articles with higher quality will be interesting here
CATEGORY_TO_ADD = "Regioni senza Citylist o Destinationlist"
DEFAULT_ACTION = AllowedActions.ADD_CAT.value

EXCEPTIONS = [  # Too small to have a citylist
    "Gibilterra",
    "Isola dei leoni marini",
    "Nananu i Ra",
    "New Island",
    "Razzoli",
    "Salt Cay",
    "Territori insulari",
]

EXCLUDED_TITLES = [
    "Atollo",
]


class MissingItemListFinder(ExistingPageBot):

    def __init__(self, custom_opts, **kwargs):
        super().__init__(**kwargs)
        self.service_cat = custom_opts.get("addcat", CATEGORY_TO_ADD)
        self.action = custom_opts.get("action", DEFAULT_ACTION)
        self.found_matches = []

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
        summary = ""
        if self.action == AllowedActions.ADD_CAT.value:
            summary = f"Aggiungo la categoria {self.service_cat}"
        elif self.action == AllowedActions.REMOVE_CAT.value:
            summary = f"Rimuovo la categoria {self.service_cat} - pagina ora con Itemlist o costituente eccezione"
        else:
            summary = "Manutenzione per regioni senza Citylist o Destinationlist"

        return {"summary": summary, "watch": "nochange", "minor": True, "bot": True}

    def handle_categorization(self):
        logging.info(f"Checking page: {self.current_page.title()} for missing Itemlist")

        # Handle exceptions
        if self.current_page.title() in EXCEPTIONS:
            logging.info(f"Skipping page {self.current_page.title()}")
            return

        # Handle excluded titles
        if any(title in self.current_page.title() for title in EXCLUDED_TITLES):
            logging.info(f"Skipping page {self.current_page.title()}")
            return

        has_citylist, has_destinationlist = self._check_relevant_templates()

        if not has_citylist and not has_destinationlist:
            logging.info(f"Page {self.current_page.title()} has no Itemlist")
            self.found_matches.append(self.current_page.title())
            if self.action == AllowedActions.ADD_CAT.value:
                self.categorize()

    def handle_decategorization(self):

        # Handle exceptions -- it could be that it was categorized by hand or with an outdated exception list
        if self.current_page.title() in EXCEPTIONS:
            logging.info(
                f"Page {self.current_page.title()} is an exception, decategorizing"
            )
            self.found_matches.append(self.current_page.title())
            if self.action == AllowedActions.REMOVE_CAT.value:
                self.remove_cat()

        # Handle excluded titles
        if any(title in self.current_page.title() for title in EXCLUDED_TITLES):
            logging.info(
                f"Page {self.current_page.title()} fulfills excluded title regex, decategorizing"
            )
            self.found_matches.append(self.current_page.title())
            if self.action == AllowedActions.REMOVE_CAT.value:
                self.remove_cat()

        # Handle normal pages
        has_citylist, has_destinationlist = self._check_relevant_templates()

        if has_citylist or has_destinationlist:
            logging.info(
                f"Page {self.current_page.title()} has Itemlist now - decategorizing"
            )
            self.found_matches.append(self.current_page.title())
            if self.action == AllowedActions.REMOVE_CAT.value:
                self.remove_cat()

    def remove_cat(self):
        self.current_page.text = self.current_page.text.replace(
            f"[[Categoria:{self.service_cat}]]", ""
        )
        # Account for cat added in English
        self.current_page.text = self.current_page.text.replace(
            f"[[Category:{self.service_cat}]]", ""
        )
        self.current_page.save(**self.edit_opts)

    def treat_page(self):

        if (
            self.action == AllowedActions.ADD_DUMP.value
            or self.action == AllowedActions.ADD_CAT.value
        ):
            self.handle_categorization()
        elif (
            self.action == AllowedActions.REMOVE_CAT.value
            or self.action == AllowedActions.REMOVE_DUMP.value
        ):
            self.handle_decategorization()
        else:
            raise ValueError(f"Invalid action: {self.action}")

    def teardown(self) -> None:
        if "dump" in self.action:
            self.dump_findings()

    @staticmethod
    def _get_template_page(template_name: str) -> pywikibot.Page:
        site = pywikibot.Site()
        page = pywikibot.Page(site, template_name, ns=10)
        return page

    def _check_relevant_templates(self) -> tuple[bool, bool]:

        citylist = MissingItemListFinder._get_template_page("Citylist")
        destinationlist = MissingItemListFinder._get_template_page("Destinationlist")

        has_citylist = False
        has_destinationlist = False

        templates = self.current_page.templates()

        for template in templates:
            if template == citylist:
                has_citylist = True
                break
            if template == destinationlist:
                has_destinationlist = True
                break

        return has_citylist, has_destinationlist

    def dump_findings(self):
        logging.info(f"Found {len(self.found_matches)} matches")
        with open(f"logs/missing_itemlits.txt", "w") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Matches for action {self.action}:\n")

            for match in self.found_matches:
                f.write(
                    f"* [[{match}]] <small>(check eseguito il {timestamp})</small>\n"
                )

    def categorize(self):
        """Add a category to the current page if it's not already present.

        :return: None
        """

        service_cat_fullname = f"Categoria:{self.service_cat}"

        if service_cat_fullname in [
            cat.title() for cat in self.current_page.categories()
        ]:
            logging.info(
                f"Category {self.service_cat} already present in {self.current_page.title()}"
            )
            return

        logging.info(
            f"Adding category {self.service_cat} to {self.current_page.title()}"
        )
        self.current_page.text += f"\n[[Categoria:{self.service_cat}]]"
        self.current_page.save(**self.edit_opts)


def handle_opts() -> list[str]:
    """
    Handles the command line options for the program
    setting the default category and activating the log.

    :return: A list of command line arguments.
    """
    args = pywikibot.handle_args()

    # set default cat, from which articles will be loaded
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

    if any(arg.startswith("-addcat") for arg in args):
        custom_opts["addcat"] = args[
            [arg.startswith("-addcat") for arg in args].index(True)
        ].split(":")[1]

    if any(arg.startswith("-action") for arg in args):
        custom_opts["action"] = args[
            [arg.startswith("-action") for arg in args].index(True)
        ].split(":")[1]

    return custom_opts


def main():
    local_args = handle_opts()
    generator, options = setup_generator(local_args)
    custom_opts = set_custom_opts(local_args)
    bot = MissingItemListFinder(generator=generator, custom_opts=custom_opts, **options)
    bot.run()


if __name__ == "__main__":
    main()
