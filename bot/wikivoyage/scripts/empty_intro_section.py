import os
import re
from datetime import datetime
import mwparserfromhell
import pywikibot
from bot.wikivoyage import WikivoyageBot
from bot.wikivoyage.aux import is_section_empty

EMPTY_DA_SAPERE_LOG = "logs/empty_da_sapere.log"


def list_empty_daSapere(lang="it"):
    """
    Run the citylist wikidata check - this will add wikidata ids to citylist items
    if the wikidata id is not already present and can be found with certainty (multiple wikidata items
    for the same city name are not allowed)
    :return: None
    """
    wikivoyage_bot = WikivoyageBot(lang=lang)

    # If log does not exist, create it
    create_log_file()

    # Example usage of listing a category
    articles = wikivoyage_bot.listify_category("Abbozzi", total=0)

    pywikibot.logging.info(f"Found {len(articles)} articles")

    # Read the text of the article
    for article in articles:
        wikivoyage_bot.set_current_page(article.title())
        pywikibot.logging.stdout(f"Checking article: {article.title()} for empty 'Da sapere' section")

        # Get and parse the page wikicode
        # updated_wikitext = wikivoyage_bot.get_page_text(article.title())
        updated_wikitext = wikivoyage_bot.get_page_text(article.title())
        wikicode = mwparserfromhell.parse(updated_wikitext)

        # Extract the templates from the page
        sections = wikicode.get_sections(levels=[2, 3], matches="Da sapere", include_headings=False)

        if len(sections) > 1 or len(sections) == 0:
            print(ValueError(f"Too many 'Da sapere' sections in {article.title()}"))
            continue

        is_empty = is_section_empty(str(sections[0]))
        if is_empty:
            write_log_entry_ifnot_exists(wikivoyage_bot)
    exit(0)


def write_log_entry_ifnot_exists(wikivoyage_bot: WikivoyageBot):
    """
    Checks if an article has been already reported in the log, and if not, writes it
    :param wikivoyage_bot:
    :param article:
    :return:
    """
    page_name = wikivoyage_bot.current_page

    # Check if the article has already been reported
    if not check_page_has_been_reported(page_name):
        current_date = datetime.now().strftime('%Y-%m-%d')
        # Write the article to the log
        wikivoyage_bot.write_log_line(
            f"* [[{page_name}]] <small>(checked on {current_date})</small>",
            file=EMPTY_DA_SAPERE_LOG,
            with_timestamp=False
        )


def create_log_file():
    if not os.path.exists(EMPTY_DA_SAPERE_LOG):
        with open(EMPTY_DA_SAPERE_LOG, "w") as f:
            f.write("")


def check_page_has_been_reported(page_name) -> bool:
    with open(EMPTY_DA_SAPERE_LOG, "r") as f:
        log = f.read()
        # Each line is in the format "* [[Page name]] <small>(checked on YYYY-MM-DD)</small>"
        # Check that the page name is in the log, independently of the date
        regex = f"\* \[\[{page_name}\]\] \<small\>\(checked on \d\d\d\d-\d\d-\d\d\)\</small\>"
        return len(re.findall(regex, log)) > 0
