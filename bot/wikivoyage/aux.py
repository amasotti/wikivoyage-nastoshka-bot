from bot.wikidata import WikidataBot


def add_wikidata_to_citylist_item(citylist, lang='it'):
    """
    Add wikidata to citylist item
    :param citylist: The list of tuples of citylist items
    :param lang: The language to use for the wikidata search, defaults to 'it'
    :return: The updated citylist
    """
    updated_citylist = []
    for city in citylist:
        city_name = city[1]['nome']
        print(f"\tAdding wikidata to citylist item: {city_name}")

        city[1]['wikidata'] = get_wikidata_entity(city_name, lang)
        updated_citylist.append(city)
    return updated_citylist


def get_wikidata_entity(city_name, lang='it'):
    wikidataBot = WikidataBot()

    # Try in italian or the language passed
    wikidata_item = wikidataBot.get_wikidata_item_for_city(city_name, lang)

    # If not found, try in english
    if wikidata_item is None:
        wikidata_item = wikidataBot.get_wikidata_item_for_city(city_name, 'en')

    if wikidata_item is None:
        print(f"Could not find wikidata item for {city_name} -- keeping empty")
        wikidata_item = ""

    return wikidata_item