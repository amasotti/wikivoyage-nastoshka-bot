import datetime
import re
from enum import Enum

import mwparserfromhell
import pywikibot
from pywikibot.bot import ExistingPageBot
from pwb_aux import setup_generator

class FileFormats(Enum):
    WIKITEXT = "wikitext"
    JSON = "json"
    TEXT = "text"

class TemplateCrossCat(ExistingPageBot):

    def __init__(self, custom_opts, **kwargs):
        super().__init__(**kwargs)
        self.target_cat = custom_opts.get("targetcat", None)

        if self.target_cat is None:
            raise ValueError("No target category specified, Use -targetcat:TargetCategory")

        self.negative = custom_opts.get("negative", False)
        self.outputfile = custom_opts.get("outputfile", "template_x_cat_results.txt")
        self.format = custom_opts.get("format", FileFormats.WIKITEXT.value)
        self.found_matches = []

    def treat_page(self):
        pywikibot.info(f"Checking page: {self.current_page.title()}")

        categories = [cat.title(with_ns=False) for cat in self.current_page.categories()]

        # We just want to create a list of all articles that are also in the target category (if self.negative is False)
        # or that are not in the target category (if self.negative is True)

        if (self.target_cat in categories) ^ self.negative:
            pywikibot.info(f"Found match: {self.current_page.title()} - this has {self.target_cat} and we are looking for {'not ' if self.negative else ''}{self.target_cat}")
            self.found_matches.append(self.current_page.title())
            pywikibot.info(f"Found match: {self.current_page.title()}")

    def teardown(self) -> None:
        self.save_results()
        super().teardown()

    def save_results(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.outputfile, "w") as f:
            if self.format == FileFormats.WIKITEXT.value:
                for match in self.found_matches:
                    f.write(f"* [[{match}]] (checked on {timestamp})\n")
            elif self.format == FileFormats.JSON.value:
                import json
                json.dump(self.found_matches, f)
            elif self.format == FileFormats.TEXT.value:
                for match in self.found_matches:
                    f.write(f"{match}\n")
            else:
                raise ValueError(f"Unknown format: {self.format}")


def set_custom_opts(args: list[str]) -> dict[str, str]:
    """
    Set custom options for the given arguments.
    """
    custom_opts = dict()

    if any(arg.startswith("-negative") for arg in args):
        custom_opts["negative"] = True

    if any(arg.startswith("-targetcat") for arg in args):
        custom_opts["targetcat"] = args[[arg.startswith("-targetcat") for arg in args].index(True)].split(":")[1]

    if any(arg.startswith("-format") for arg in args):
        custom_opts["format"] = args[[arg.startswith("-format") for arg in args].index(True)].split(":")[1]

    if any(arg.startswith("-outputfile") for arg in args):
        custom_opts["outputfile"] = args[[arg.startswith("-outputfile") for arg in args].index(True)].split(":")[1]

    return custom_opts


def main():
    local_args = pywikibot.handle_args()
    generator, options = setup_generator(local_args)
    custom_opts = set_custom_opts(local_args)
    bot = TemplateCrossCat(generator=generator, custom_opts=custom_opts, **options)
    bot.run()


if __name__ == '__main__':
    main()
