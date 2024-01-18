import datetime
import re

import mwparserfromhell
import pywikibot
from pywikibot.bot import ExistingPageBot
from pwb_aux import setup_generator

SOURCE_CATEGORY = "Abbozzi"  # Very unlikely that articles with higher quality will be interesting here
CATEGORY_TO_ADD = "Articoli senza introduzione"
SECTION_NAME = "Da sapere"
DEFAULT_ACTION = "dump"  # "dump" or "addcat"


class EmptySectionFinder(ExistingPageBot):

    def __init__(self, custom_opts, **kwargs):
        super().__init__(**kwargs)
        self.service_cat = custom_opts.get("addcat", CATEGORY_TO_ADD)
        self.section_name = custom_opts.get("section", SECTION_NAME)
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
                 - "botflag": A boolean indicating whether the edit should be flagged as a bot edit (default: True).
        """
        return {
            "summary": f"Sezione {self.section_name} vuota - categorizzo",
            "watch": "nochange",
            "minor": True,
            "botflag": True
        }

    def treat_page(self):
        pywikibot.info(f"Checking page: {self.current_page.title()} for empty '{self.section_name}' section")

        content = self.current_page.text
        wikicode = mwparserfromhell.parse(content)

        sections = wikicode.get_sections(matches=self.section_name, include_headings=False)

        # Make sure we found the standard section with this name
        # there should be only 1 per page
        n_sections = len(sections)

        if n_sections > 1 or n_sections == 0:
            pywikibot.warning(f"Too many '{self.section_name}' sections in {self.current_page.title()}")
            return

        # Get the section text
        target_section = sections[0]
        is_empty = EmptySectionFinder.is_section_empty(str(target_section))

        if is_empty:
            pywikibot.info(f"Found empty '{self.section_name}' section in {self.current_page.title()}")

            if self.action == "dump":
                pywikibot.output("Found empty section in page:")
                pywikibot.output(self.current_page.title())
                self.found_matches.append(self.current_page.title())
            elif self.action == "addcat":
                self.add_category()

    def teardown(self) -> None:
        if self.action == "dump":
            self.dump_findings()

    def dump_findings(self):
        pywikibot.info(f"Found {len(self.found_matches)} matches")
        with open("logs/empty_sections.txt", "w") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            f.write(f"Empty sections dump - {timestamp}\n")
            f.write(f"Found {len(self.found_matches)} matches\n\n")
            f.write("Searched for:\n")
            f.write(f"Section name: {self.section_name}\n")
            f.write(f"Service category: {self.service_cat}\n\n")
            f.write("Matches:\n")

            for match in self.found_matches:
                f.write(f"* [[{match}]] <small>(check eseguito il {timestamp})</small>\n")

    def add_category(self):
        """
        Adds the service category to the page, if not already present.
        """

        service_cat_fullname = f"Categoria:{self.service_cat}"

        if service_cat_fullname in [cat.title() for cat in self.current_page.categories()]:
            pywikibot.info(f"Category {self.service_cat} already present in {self.current_page.title()}")
            return

        pywikibot.info(f"Adding category {self.service_cat} to {self.current_page.title()}")
        self.current_page.text += f"\n[[Categoria:{self.service_cat}]]"
        self.current_page.save(**self.edit_opts)

    @staticmethod
    def is_section_empty(section_text):
        # Remove comments
        text_without_comments = re.sub(r'<!--.*?-->', '', section_text,
                                       flags=re.DOTALL | re.MULTILINE | re.UNICODE | re.IGNORECASE)

        # Remove spacing templates
        text_without_spacing = re.sub(r'\{\{-\}\}', '', text_without_comments)

        # Remove newlines
        text_without_spacing = text_without_spacing.replace('\n', '')

        # Check if there's any content left
        return not text_without_spacing.strip()


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
    custom_opts = dict()

    if any(arg.startswith("-addcat") for arg in args):
        custom_opts["addcat"] = args[[arg.startswith("-addcat") for arg in args].index(True)].split(":")[1]

    if any(arg.startswith("-section") for arg in args):
        custom_opts["section"] = args[[arg.startswith("-section") for arg in args].index(True)].split(":")[1]

    if any(arg.startswith("-action") for arg in args):
        custom_opts["action"] = args[[arg.startswith("-action") for arg in args].index(True)].split(":")[1]

    return custom_opts


def main():
    local_args = handle_opts()
    generator, options = setup_generator(local_args)
    set_custom_opts(local_args)
    custom_opts = set_custom_opts(local_args)
    bot = EmptySectionFinder(generator=generator, custom_opts=custom_opts, **options)
    bot.run()


if __name__ == '__main__':
    main()
