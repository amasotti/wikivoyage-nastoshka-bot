from datetime import datetime
import mwparserfromhell
import pywikibot
from bot.wikivoyage import WikivoyageBot

def run_citylist_wikidata_check():
    """
    Run the citylist wikidata check - this will add wikidata ids to citylist items
    if the wikidata id is not already present and can be found with certainty (multiple wikidata items
    for the same city name are not allowed)
    :return: None
    """
    wikivoyage_bot = WikivoyageBot(lang="it")

    # Example usage of listing a category
    articles = wikivoyage_bot.listify_category("Itemlist con errori di compilazione", 1)

    # Read the text of the article
    for article in articles:
        wikivoyage_bot.set_current_page(article.title())
        pywikibot.logging.stdout(f"Checking article: {article.title()}")

        # Get and parse the page wikicode
        updated_wikitext = wikivoyage_bot.get_page_text(article.title())
        wikicode = mwparserfromhell.parse(updated_wikitext)

        # Extract the templates from the page
        templates = wikicode.filter_templates()

        # Add wikidata ids to the templates if they are missing and can be found
        wikivoyage_bot.process_wikidata_in_citylist(templates)

        # Save the page
        page = wikivoyage_bot.get_page(article.title())
        updated_wikitext = str(wikicode)
        page.text = updated_wikitext
        page.save("Aggiungo wikidata ids",
                  watch='watch',
                  minor=True,
                  )
        wikivoyage_bot.write_log_line(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {article.title()} -- Added wikidata ids\n")
    exit(0)