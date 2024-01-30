import re
from enum import Enum

import pywikibot


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


