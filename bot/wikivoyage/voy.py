import re
import pywikibot
from pywikibot import Page
from pywikibot import textlib


def login(lang="it"):
    """
    Login to Wikivoyage
    :param lang: language code
    :return: pywikibot.Site
    """
    return pywikibot.Site(code=lang, fam="wikivoyage")



def listify_cat(site, cat_name):
    """
    Listify a category
    :param cat_name:
    :param lang:
    :return:
    """
    category = pywikibot.Category(site,title=cat_name)
    category.articles()
    return list(category.articles(total=4))


def get_used_by(site, article, total=3):
    """
    Get pages that use a template
    :param site: pywikibot.Site
    :param article: str
    :param total: int
    :return: list of pywikibot.Page
    """
    page = pywikibot.Page(site,title=article, ns=10) # ns=10 is the template namespace
    linked_pages = page.getReferences(
        namespaces=0, # Restrict to main namespace
        total=total, # Only retrieve x pages
        only_template_inclusion=True)
    return list(linked_pages)


def get_page_text(site, page_name) -> Page.text:
    page = pywikibot.Page(site, title=page_name)
    return page.text

def parse_nested_template(wikitext: Page.text, template_name: str):
    # Find the start of the template
    parsed_data = textlib.extract_templates_and_params(wikitext, True, True)


    # Filter only the template we want
    parsed_data = [x for x in parsed_data if x[0] == template_name]

    return parsed_data

def parse_listed_destinations(wikitext):
    return parse_nested_template(wikitext, 'Destinazione')

def parse_listed_cities(wikitext):
    return parse_nested_template(wikitext, 'Città')

