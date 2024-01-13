import random

from bot.wikivoyage.VoyBot import WikivoyageBot


# def main():
#     site = login()
#     # template = "Citylist"
#     # articles = get_used_by(site,template)
#     # for article in articles:
#     #     print(article.title())
#
#     testo = get_page_text(site, "Germania")
#     destinazioni = parse_listed_cities(testo)
#     # for destinazione in destinazioni:
#     #     print(destinazione)
#
#     # Get the last one in the list
#     last_destinazione = destinazioni[-1]
#     last_destinazione[1]["wikidata"] = "Q1234"
#     print(last_destinazione[1]['nome'])
#     print(last_destinazione[1]['wikidata'])
#     print(last_destinazione)

def main():
    wikivoyage_bot = WikivoyageBot(lang="it")

    # Example usage of listing a category
    articles = wikivoyage_bot.get_pages_using_template("Citylist",3)
    print(articles)

    # Example usage of parsing a page for destinations or cities
    page_text = wikivoyage_bot.get_page_text(articles[0].title())
    cities = wikivoyage_bot.parse_listed_cities(page_text)
    print(cities)


if __name__ == "__main__":
    main()