import pywikibot
from pywikibot import textlib

class WikiBot:
    def __init__(self, lang="it", fam="wikivoyage"):
        self.site = pywikibot.Site(code=lang, fam=fam)

    def get_page_text(self, p_name, namespace=0):
        """
        Get the raw wiki text of a page
        :param p_name: str, page title
        :param namespace: int, namespace, defaults to 0 (main)
        :return: raw wiki text
        """
        page = self.get_page(p_name,ns=namespace)
        return page.text

    def get_page(self, page_name, ns=0) -> pywikibot.Page:
        """
        Get a pywikibot.Page object
        :param page_name: str page name
        :param ns: int namespace, defaults to 0 (main)
        :return: pywikibot.Page object
        """
        return pywikibot.Page(self.site, title=page_name, ns=ns)

    def listify_category(self, cat_name, total=4):
        """
        Given a category name, get the pages that are in it
        :param cat_name:
        :param total:
        :return:
        """
        category = pywikibot.Category(self.site, title=cat_name)
        return list(category.articles(recurse=True, total=total))
