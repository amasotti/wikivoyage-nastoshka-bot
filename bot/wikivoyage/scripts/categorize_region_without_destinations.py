import pywikibot.logging

from bot.wikivoyage import WikivoyageBot


def categorize_region_without_destinations(target="Stato"):
    bot = WikivoyageBot(lang="it")

    citylist = bot.get_template("Citylist")
    destinationlist = bot.get_template("Destinationlist")

    # 1. Retrieve all regions and states articles
    articles = bot.listify_category(target,0)
    total_articles = len(articles)

    # 2. Check if there is a Citylist or Destinationlist template in the article (exclude comments)
    to_be_categorized = []
    i = 0
    for article in articles:
        i += 1
        print(f"Processing article {i} of {total_articles}")

        bot.set_current_page(article.title())

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

        if not has_citylist and not has_destinationlist:
            pywikibot.logging.info(f"Article {article.title()} has no Citylist or Destinationlist template")
            to_be_categorized.append(article.title())
            if bot.is_in_category(article.title(), "Categoria:Regioni senza Citylist o Destinationlist"):
                continue
            else:
                bot.add_category(bot.current_page, "Regioni senza Citylist o Destinationlist")
        bot.set_current_page(None)
    # 3. Dump a list of these articles to a file
    bot.write_log_line("Articles without Citylist or Destinationlist templates:", "logs/region_without_destinations.log")
    for article in to_be_categorized:
        bot.write_log_line(
            f"* [[{article}]]",
            "logs/region_without_destinations.log", with_timestamp=False)

    # 4. Categorize the article in Category:Regions without destinations

