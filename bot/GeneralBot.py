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
        page = pywikibot.Page(self.site, title=p_name, ns=namespace)
        page.templates()
        return page.text

    def get_page(self, page_name, ns=0) -> pywikibot.Page:
        """
        Get a pywikibot.Page object
        :param page_name: str page name
        :param ns: int namespace, defaults to 0 (main)
        :return: pywikibot.Page object
        """
        return pywikibot.Page(self.site, title=page_name, ns=ns)

    def get_template(self, template_name, ns=10) -> pywikibot.Page:
        """
        Get a pywikibot.Page object
        :param template_name: str template name
        :param ns: int namespace, defaults to 10 (template)
        :return: pywikibot.Page object
        """
        return pywikibot.Page(self.site, title=template_name, ns=ns)

    def get_page_templates(self, p_name, namespace=0):
        """
        Get the templates used in a page
        :param p_name: str, page title
        :param namespace: int, namespace, defaults to 0 (main)
        :return: list of templates
        """
        page = pywikibot.Page(self.site, title=p_name, ns=namespace)
        return page.templatesWithParams()

    def get_template_usage(self, template_name, total=3, namespace=0):
        """
        Given a template name, get the pages that use it by embedding it
        :param template_name: str, template name
        :param total: int, total number of pages to return, defaults to 3
        :param namespace:  int, namespace, defaults to 0 (main)
        :return: list of pages
        """
        template_page = pywikibot.Page(self.site, title=template_name, ns=10)
        linked_pages = template_page.getReferences(
            namespaces=namespace,
            total=total,
            only_template_inclusion=True)
        return list(linked_pages)

    def listify_category(self, cat_name, total=4):
        """
        Given a category name, get the pages that are in it
        :param cat_name:
        :param total:
        :return:
        """
        category = pywikibot.Category(self.site, title=cat_name)
        return list(category.articles(recurse=True, total=total))

    def parse_nested_template(self, wikitext, template_name):
        parsed_data = textlib.extract_templates_and_params(wikitext, True, True)
        return [x for x in parsed_data if x[0] == template_name]

    def add_category(self, page_name, category_name):
        page = pywikibot.Page(self.site, title=page_name)
        page.text = page.text + f"\n[[Categoria:{category_name}]]"
        page.save(f"Aggiungo categoria {category_name}",minor=True, botflag=True, watch="nochange")
