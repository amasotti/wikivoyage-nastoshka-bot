from bot.wikivoyage import *


def main():
    site = login()
    # template = "Citylist"
    # articles = get_used_by(site,template)
    # for article in articles:
    #     print(article.title())

    testo = get_page_text(site, "Germania")
    destinazioni = parse_listed_cities(testo)
    # for destinazione in destinazioni:
    #     print(destinazione)

    # Get the last one in the list
    last_destinazione = destinazioni[-1]
    last_destinazione[1]["wikidata"] = "Q1234"
    print(last_destinazione[1]['nome'])
    print(last_destinazione[1]['wikidata'])
    print(last_destinazione)



if __name__ == "__main__":
    main()