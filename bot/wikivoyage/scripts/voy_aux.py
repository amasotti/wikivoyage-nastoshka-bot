import re
from enum import Enum
from typing import Iterable
import pywikibot
from mwparserfromhell.nodes import Template
from mwparserfromhell.wikicode import Wikicode


class ArticleTypes(Enum):
    CITY = "city"
    REGION = "region"
    COUNTRY = "country"
    DISTRICT = "district"
    PARK = "park"
    ARCHEOLOGICAL_SITE = "archeological_site"


class ArticleTypeCategories(Enum):
    CITY = "Città"
    REGION = "Regione"
    COUNTRY = "Stato"
    DISTRICT = "Distretto"
    PARK = "Parco"
    ARCHEOLOGICAL_SITE = "Sito Archeologico"


class ArticleTypeLookup:
    _article_type_lookup = {
        ArticleTypeCategories.CITY.value: ArticleTypes.CITY,
        ArticleTypeCategories.REGION.value: ArticleTypes.REGION,
        ArticleTypeCategories.COUNTRY.value: ArticleTypes.COUNTRY,
        ArticleTypeCategories.DISTRICT.value: ArticleTypes.DISTRICT,
        ArticleTypeCategories.PARK.value: ArticleTypes.PARK,
        ArticleTypeCategories.ARCHEOLOGICAL_SITE.value: ArticleTypes.ARCHEOLOGICAL_SITE
    }

    @classmethod
    def get_article_type(cls, page: pywikibot.Page) -> ArticleTypes:
        cats = page.categories()
        for cat in cats:
            cat_title = cat.title(with_ns=False)
            if cat_title in cls._article_type_lookup:
                return cls._article_type_lookup[cat_title]
        raise ValueError(f"Could not find article type for page {page.title()}")


def format_quickbar(line):
    return re.sub(r'\|\s*([^=]+?)\s*=\s*(.*?)\s*(?=\||$)', r'| \1 = \2', line)


def format_listing(line):
    return re.sub(r'\|\s*([^=]+)\s*=\s*(.*?)\s*(?=[|\n])', r'| \1=\2 ', line)


def format_inline(line):
    return re.sub(r'\|\s*([^=]+)\s*=\s*', r'| \1=', line.strip())


def format_template_params(text):
    """
    Format template parameters in the text for specific templates.

    Args:
        text (str): The wikitext to process.

    Returns:
        str: The text with formatted template parameters.
    """

    # Define templates and their formatting functions
    templates = {
        'quickbarairport': format_quickbar,
        'see': format_listing,
        'do': format_listing,
        'eat': format_listing,
        'buy': format_listing,
        'sleep': format_listing,
        'drink': format_listing,
        'listing': format_listing,
        'marker': format_inline,
        'Destinazione': format_inline,
        'Città': format_inline,
        'Destinationlist': format_quickbar,
        'Regionlist': format_quickbar,
        'MappaDinamica': format_quickbar,
    }

    def format_params(match):
        template_name = match.group(1).strip()
        format_function = templates.get(template_name.lower())

        if not format_function:
            return match.group(0)

        params = match.group(2)
        param_lines = params.split('\n')
        formatted_lines = [format_function(line) for line in param_lines]

        formatted_params = ' '.join(formatted_lines) if format_function == format_inline else '\n'.join(formatted_lines)
        template_format = '{{' + template_name + '{}{}'.format('\n' if format_function != format_inline else ' ',
                                                               formatted_params) + '}}'

        return template_format

    template_pattern = r'\{\{\s*([^}|]+)\s*(\|[^}]+)\}\}'
    formatted_text = re.sub(template_pattern, format_params, text, flags=re.IGNORECASE)

    return formatted_text


def terminate_before_section_level_two(text: str, exception: str = ["Da sapere"]) -> str:
    """
    Add {{-}} directly after the text preceding a level two section, followed by one newline.

    Args:
        text (str): The wikitext to process.

    Returns:
        str: The text with {{-}} added before level two sections.
    """
    section_pattern = r'(.*?)(\n*)(?<!\=)==\s*([^=].*?)\s*==(?!=)'

    def replace_section(match):
        preceding_text = match.group(1)  # Extract the text preceding the section
        section_title = match.group(3)  # Extract the section title

        # Check if the section title is not "Voli"
        if section_title.strip().lower() not in [exc.lower() for exc in exception]:
            # Add {{-}} directly after the preceding text, followed by one newline,
            return preceding_text + "\n{{-}}\n\n== " + section_title + " =="
        else:
            # If the section title is "Voli", return the text without modification
            return preceding_text + "\n\n== " + section_title + " =="

    # Use the sub() function to replace the matched text with the formatted replacement
    formatted_text = re.sub(section_pattern, replace_section, text, flags=re.DOTALL)

    return formatted_text


def add_banner_image(templates: Iterable[Template], image: str):
    for template in templates:
        if template.name.lower() == "Quickbar\n":
            template.add("Banner", image)
            break


def add_quickbar_image(templates: Iterable[Template], image: str) -> str:
    for template in templates:
        if template.name.lower() == "Quickbar\n":
            template.add("Immagine", image)
            break


def add_mappa_dinamica(page_text: Wikicode, templates: Iterable[Template], coords, zoom=8):
    # If there is already a dynamic map, ignore the rest
    if _check_mappa_dinamica_exist(templates):
        return

    # If there is a region list, just add the dynamic map
    try:
        if _check_region_list_exist(templates):
            for template in templates:
                try:
                    if template.name == "Regionlist\n":
                        template.add("regionInteractiveMap", "map1", before=template.get("region1name"))
                        template.add("regionmapLat", coords["lat"], preserve_spacing=True, before=template.get("region1name"))
                        template.add("regionmapLong", coords["long"], preserve_spacing=True, before=template.get("region1name"))
                        template.add("regionmapsize", "450px", preserve_spacing=True, before=template.get("region1name"))
                        template.add("regionmapZoom", str(zoom) + "\n\n", preserve_spacing=True, before=template.get("region1name"))
                        break
                except:
                    pywikibot.error("Error adding dynamic map to region list, template: " + str(template))
                    raise ValueError("Error adding dynamic map to region list")
        else:
            # If there is no region list and no dynamic map, add the dynamic map and the region list
            template = Template("MappaDinamica\n")
            try:
                template.add("Lat", coords["lat"] + "\n", preserve_spacing=False)
                template.add("Long", coords["long"] + "\n", preserve_spacing=False)
                template.add("h", "450", preserve_spacing=False)
                template.add("w", "450", preserve_spacing=False)
                template.add("z", str(zoom), preserve_spacing=False)
                template.add("view", "Kartographer\n", preserve_spacing=False)
            except:
                pywikibot.error("Error creating dynamic map template for page: " + str(template))
                raise ValueError("Error creating dynamic map template")

            sections = page_text.get_sections(levels=[2], flat=True)
            for section in sections:
                try:
                    if section.get(0) == "== Territori e mete turistiche ==":
                        mappa_str = "\n" + str(template) + "\n"
                        section.insert(2, mappa_str)
                        break
                except:
                    continue
    except:
        pywikibot.error("Error adding dynamic map to page: ")

def _check_mappa_dinamica_exist(templates: Iterable[Template]) -> bool:
    for template in templates:
        if template.name == "MappaDinamica\n":
            return True
    return False


def _check_region_list_exist(templates: Iterable[Template]) -> bool:
    for template in templates:
        if template.name == "Regionlist\n" and not template.has("regionInteractiveMap"):
            return True
    return False


def format_section_begin(text: str) -> str:
    section_pattern = r'(?<!\=)==\s*([^=].*?)\s*==(?!=)(.*?)\n(?!$)'
    formatted_text = re.sub(section_pattern, r'== \1 ==\n\2\n', text, flags=re.DOTALL)

    return formatted_text


def format_section_titles(text):
    """
    Ensure there is a space between the series of equal signs and the section title.

    Args:
        text (str): The wikitext to process.

    Returns:
        str: The text with formatted section titles.
    """

    # Define the regex pattern for matching section titles of all levels
    section_pattern = r'(={2,})\s*(.*?)\s*\1'

    # Function to format section titles
    def format_title(match):
        equal_signs = match.group(1)  # Extract the series of equal signs
        title = match.group(2).strip()  # Extract and strip the section title

        # Format the section title with spaces between equal signs and the title
        return f'{equal_signs} {title} {equal_signs}'

    # Use the sub() function to replace the matched text with formatted section titles
    formatted_text = re.sub(section_pattern, format_title, text)

    return formatted_text
