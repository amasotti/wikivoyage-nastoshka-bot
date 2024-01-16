import mwparserfromhell
from bot.wikivoyage import WikivoyageBot
import pywikibot


def check_coords_dynamic_maps(lang="it", total=1):
    """
    In some - few articles - there is a dynamic map but this has no coordinates.
    This script checks for such articles, gets the coordinates from Wikidata and adds them to the article.
    :return:
    """

    bot = WikivoyageBot(lang=lang)

    articles_with_map = bot.listify_category("Mappa dinamica senza coordinate", int(total))

    for article in articles_with_map:
        bot.set_current_page(article.title())
        pywikibot.logging.info(f"Checking article: {bot.current_page}")

        text = bot.get_page_text(bot.current_page)
        wikicode = mwparserfromhell.parse(text)

        templates = wikicode.filter_templates()

        bot.process_dynamicMap_without_coordinates(templates)

        page = bot.get_page(bot.current_page)
        updated_wikitext = str(wikicode)

        page.text = updated_wikitext
        pywikibot.logging.info(f"Saving page {bot.current_page}")
        pywikibot.logging.info("-".join(["-"] * 20))
        #pywikibot.showDiff(text, updated_wikitext)
        page.save(f"Aggiungo le coordinate alla mappa dinamica di {bot.current_page}",
                  watch='nochange',
                  minor=True,
                  )