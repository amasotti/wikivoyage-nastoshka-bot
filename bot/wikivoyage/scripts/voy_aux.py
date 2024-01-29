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


def format_template_params(text):
    """
    Format template parameters in the text for specific templates.

    Args:
        text (str): The wikitext to process.

    Returns:
        str: The text with formatted template parameters.
    """

    # Define templates and their formatting styles
    templates = {
        'quickbarairport': 'quickbar',
        'see': 'listing',
        'do': 'listing',
        'eat': 'listing',
        'buy': 'listing',
        'sleep': 'listing',
        'drink': 'listing',
        'listing': 'listing',
        'marker': 'inline',
    }

    # Function to format parameters based on the template style
    def format_params(match):
        template_name = match.group(1).strip()  # Extract and strip the template name
        style = templates.get(template_name.lower(), None)  # Determine the formatting style

        # Skip processing if the template style is not recognized
        if style is None:
            return match.group(0)

        params = match.group(2)  # Extract parameters string only if style is recognized
        param_lines = params.split('\n')  # Split parameters by newline to preserve them

        # Process each line separately to preserve newlines
        formatted_lines = []
        for line in param_lines:
            if style == 'quickbar':
                # Adjusted format for quickbar: | param = value with single space around '='
                formatted_line = re.sub(r'\|\s*([^=]+?)\s*=\s*(.*?)\s*(?=\||$)', r'| \1 = \2', line)
            elif style == 'listing':
                # Format for listing templates: | param=value (no space around '=')
                formatted_line = re.sub(r'\|\s*([^=]+)\s*=\s*(.*?)\s*(?=[|\n])', r'| \1=\2 ', line)
            elif style == 'inline':
                # All parameters are kept on the same line
                formatted_line = re.sub(r'\|\s*([^=]+)\s*=\s*', r'| \1=', line.strip())
                # Join all formatted lines with a space instead of a newline

            formatted_lines.append(formatted_line)
        if style != 'inline':
            # Join the processed lines back together, preserving newlines
            formatted_params = '\n'.join(formatted_lines)
        else:
            formatted_params = ' '.join(formatted_lines)

        # Add a newline character after the template name
        if style == 'quickbar':
            return '{{' + template_name + '\n' + formatted_params + '}}'
        elif style == 'inline':
            return '{{' + template_name + formatted_params + '}}'
        elif style == 'listing':
            return '{{' + template_name + '\n' + formatted_params + '}}'
        return match.group(0)

    # Define the regex pattern for matching templates and their parameters
    template_pattern = r'\{\{\s*([^}|]+)\s*(\|[^}]+)\}\}'

    # Use the sub() function to replace the matched text with formatted parameters
    formatted_text = re.sub(template_pattern, format_params, text, flags=re.IGNORECASE)

    return formatted_text


def terminate_before_section_level_two(text: str, exception: str =["Da sapere"]) -> str:
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
