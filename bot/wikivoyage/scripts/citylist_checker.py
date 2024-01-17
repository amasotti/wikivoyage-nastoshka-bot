from datetime import datetime
import mwparserfromhell
import pywikibot
from bot.wikivoyage import WikivoyageBot


def citylist_wikidata_check(lang="it", total=1):
    """
    Run the citylist wikidata check - this will add wikidata ids to citylist items
    if the wikidata id is not already present and can be found with certainty (multiple wikidata items
    for the same city name are not allowed)
    :return: None
    """
    voy_bot = WikivoyageBot(lang=lang)

    # Example usage of listing a category
    articles = voy_bot.listify_category("Itemlist con errori di compilazione", total)

    # Read the text of the article
    for article in articles:
        voy_bot.set_current_page(article.title())
        #voy_bot.set_current_page("Provincia di Como")
        pywikibot.logging.stdout(f"Checking article: {voy_bot.current_page}")

        # Get and parse the page wikicode
        updated_wikitext = voy_bot.get_page_text(voy_bot.current_page)
        wikicode = mwparserfromhell.parse(updated_wikitext)

        # Extract the templates from the page
        templates = wikicode.filter_templates()

        # Add wikidata ids to the templates if they are missing and can be found
        voy_bot.process_wikidata_in_citylist(templates)

        # Save the page
        page = voy_bot.get_page(voy_bot.current_page)
        updated_wikitext = str(wikicode)
        page.text = updated_wikitext
        page.save(f"Aggiungo wikidata ids ai template citylist e destinationlist",
                  watch='nochange',
                  minor=True,
                  )
        # Log the operation
        voy_bot.write_log_line(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {article.title()} -- Added wikidata ids\n")

        # Reset the current page
        voy_bot.set_current_page(None)
    exit(0)
