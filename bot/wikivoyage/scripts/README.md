# Wikivoyage scripts

This directory lists the scripts used to operate on Wikivoyage data and their documentation.

## Scripts

1. [itemlist_wikidata_completer](itemlist_wikidata_completer.py) - [Docs](MissingItemlistFinder.md) Finds itemlists without wikidata params and fills them.
2. [apply_airport_model](apply_airport_model.py) (Not documented) - Applies the airport model to Wikivoyage articles in a given category.
3. [complete_table_best_images](complete_table_best_images.py) (not documented) - Substitutes local with images from Commons in a table given a page name
4. [empty_section_fider](empty_section_finder.py) - [Docs](EmptySectionFinder.md) Finds empty sections in Wikivoyage articles, given a cat and section name.
5. [fix_empty_dynami_map](fix_empty_dynamic_map.py) - [Docs](DynamicMapFiller.md)  Fixes empty dynamic maps in Wikivoyage articles, getting coordinates from Wikidata.
6. [list_articles_without_map](list_articles_without_map.py) - (Not documented) - Lists articles without a dynamic map but with a regionlist / citylist.
7. [missing_itemlist_finder](missing_itemlist_finder.py) - [Docs](MissingItemlistFinder.md) Finds region or state articles without a list of cities or destinations (or with just plaintext)
8. [update_mapcode_quickbar](update_mapcode_quickbar.py) - [Docs](UpdateMapcodeQuickbar.md) Updates the mapcode in the quickbar of Wikivoyage articles, substituting the old code with the new one given by the user.
9. [template_x_cat](template_x_cat.py) - (Not documented) - Utility to find all pages used by a template, but (not) in a given category.


## Utilities

- [PWB AUX](pwb_aux.py) - Auxiliary functions for the scripts
- [Wikibase Helper](WikibaseHelper.py) - Collection of functions to interact with Wikibase