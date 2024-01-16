import pywikibot.logging
from pywikibot import sleep

from bot.wikivoyage import WikivoyageBot

LOG_FILE_PATH = "logs/region_without_destinations.log"


def categorize_region_without_destinations(target="Stato"):
    bot = WikivoyageBot(lang="it")
    articles = bot.listify_category(target, 0)

    # Initialize a list of articles to be categorized
    to_be_categorized = []

    for i, article in enumerate(articles, start=1):
        print(f"Processing article {i} of {len(articles)}")
        bot.set_current_page(article.title())
        has_citylist, has_destinationlist = _check_relevant_templates(bot, article)

        if not has_citylist and not has_destinationlist:
            pywikibot.logging.info(f"Article {article.title()} has no Citylist or Destinationlist template")
            to_be_categorized.append(article.title())
            if not bot.is_in_category(article.title(), "Categoria:Regioni senza Citylist o Destinationlist"):
                bot.add_category(bot.current_page, "Regioni senza Citylist o Destinationlist")
                sleep(10)
        bot.set_current_page(None)
    # Dump a list of these articles to a file
    bot.write_log_line(f"Articles of type {target} without Citylist or Destinationlist templates:", LOG_FILE_PATH)
    bot.write_log_line(
        '\n'.join([f"* [[{article}]]" for article in to_be_categorized]),
        LOG_FILE_PATH, with_timestamp=False)


def _check_relevant_templates(bot, article):
    """
    Check if the specified article has specific templates.

    :param bot: The instance of the bot.
    :type bot: Bot
    :param article: The title of the article to check.
    :type article: str
    :return: A tuple indicating whether the article has Citylist template and Destinationlist template respectively.
    :rtype: tuple
    """
    citylist = bot.get_template("Citylist")
    destinationlist = bot.get_template("Destinationlist")

    has_citylist = False
    has_destinationlist = False

    templates = bot.get_page_templates(bot.current_page)

    for template in templates:
        template_page, params = template
        if template_page == citylist:
            has_citylist = True
            break
        if template_page == destinationlist:
            has_destinationlist = True
            break
    return has_citylist, has_destinationlist
