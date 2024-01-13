from pywikibot import textlib

from bot.wikivoyage import WikivoyageBot
from bot.wikivoyage import add_wikidata_to_citylist_item

def main():
    wikivoyage_bot = WikivoyageBot(lang="it")

    # Example usage of listing a category
    articles = wikivoyage_bot.get_pages_using_template("Citylist",5)
    print(articles)

    # Example usage of parsing a page for destinations or cities
    page_text = wikivoyage_bot.get_page_text(articles[0].title())
    cities = wikivoyage_bot.parse_listed_cities(page_text)

    updated_cities = add_wikidata_to_citylist_item(cities)

    for city in updated_cities:
        print(textlib.glue_template_and_params(city).replace("\n", " "))


if __name__ == "__main__":
    main()