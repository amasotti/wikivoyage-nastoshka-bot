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