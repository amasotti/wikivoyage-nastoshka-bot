from bot.wikidata import WikidataBot
import re

def add_wikidata_to_citylist_item(citylist, lang='it'):
    """
    Add wikidata to citylist item
    :param citylist: The list of tuples of citylist items
    :param lang: The language to use for the wikidata search, defaults to 'it'
    :return: The updated citylist
    """
    updated_citylist = []
    for city in citylist:
        # If wikidata exists as key in the ordered dict, skip
        if 'wikidata' in city[1] and city[1]['wikidata'] != '':
            updated_citylist.append(city)
            continue

        city_name = city[1]['nome']
        city_alt_name = city[1]['alt']
        print(f"\tAdding wikidata to citylist item: {city_name}")

        city[1]['wikidata'] = get_wikidata_entity(city_name, city_alt_name, lang)
        updated_citylist.append(city)
    return updated_citylist


def get_wikidata_entity(article_name, alt, lang='it'):
    wikidataBot = WikidataBot()

    # Try in italian or the language passed
    wikidata_item = wikidataBot.run_query(article_name, lang)

    # If not found, try in english
    if wikidata_item is None:
        wikidata_item = wikidataBot.run_query(article_name, 'en')

    # One last try with the alt name
    if wikidata_item is None:
        wikidata_item = wikidataBot.run_query(alt, 'en')

    if wikidata_item is None:
        print(f"\t\tCould not find wikidata item for {article_name} -- keeping empty")
        wikidata_item = ""

    return wikidata_item

def glue_voy_destination_template(template_and_params):
    template, params = template_and_params

    # Define the order for known keys and ensure they are in params
    known_keys = ['nome', 'alt', 'wikidata', 'lat', 'long', 'descrizione']
    params_with_defaults = {key: params.get(key, '') for key in known_keys}

    # Build the template text for known keys
    text = ' | '.join(f'{key}={params_with_defaults[key]}' for key in known_keys)

    # Append additional parameters that are not in known_keys
    additional_params = {k: v for k, v in params.items() if k not in known_keys}
    additional_text = ' | '.join(f'{key}={value}' for key, value in additional_params.items())

    # Combine known keys text and additional parameters text
    combined_text = ' | '.join(filter(None, [text, additional_text]))
    return f'{{{{{template} | {combined_text}}}}}'

def is_section_empty(section_text):
    # Remove comments
    text_without_comments = re.sub(r'<!--.*?-->', '', section_text, flags=re.DOTALL)
    # Remove spacing templates
    text_without_spacing = re.sub(r'\{\{-\}\}', '', text_without_comments)

    # Remove newlines
    text_without_spacing = text_without_spacing.replace('\n', '')
    # Check if there's any content left
    return not text_without_spacing.strip()

def has_template(page, template):
    return template in page.templates()