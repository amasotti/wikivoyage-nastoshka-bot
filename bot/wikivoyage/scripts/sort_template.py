import mwparserfromhell

from bot.wikivoyage import WikivoyageBot


def sort_template_params(page_name: str, template_name: str, lang: str = "it"):
    wikivoyage_bot = WikivoyageBot(lang=lang)
    sorting_strategy = select_sorting_strategy(template_name)

    # Example usage of listing a category
    article = wikivoyage_bot.get_page(page_name)
    wikivoyage_bot.set_current_page(article.title())

    text = article.text
    wikicode = mwparserfromhell.parse(text)

    templates = wikicode.filter_templates()

    for template in templates:
        if template.name.matches(template_name):
            sorting_strategy(template)

    # Save the page
    article.text = str(wikicode)
    article.save(f"Ordino alfabeticamente i parametri del template {template_name} di {page_name}",
                watch='watch',
                minor=True,
                )


def select_sorting_strategy(template_name: str):
    strategies = {
        "Citylist": sort_citylist,
        "Destinationlist": sort_citylist,
        # Add more templates and their corresponding sorting functions here
    }
    if template_name not in strategies:
        raise NotImplementedError(f"Sorting strategy for template {template_name} not implemented")
    return strategies[template_name]


def sort_citylist(template, sorting_key="nome"):
    # Extracting nested templates (Città) from the Citylist template
    nested_templates = [param.value.filter_templates()[0] for param in template.params if param.value.filter_templates()]

    # Sorting the nested templates based on the specified key
    sorted_nested_templates = sorted(nested_templates, key=lambda x: x.get(sorting_key).value.strip() if x.has_param(sorting_key) else "")

    # Reconstructing the Citylist template with sorted nested templates
    for i, nested_template in enumerate(sorted_nested_templates, start=1):
        template.add(str(i), str(nested_template))

