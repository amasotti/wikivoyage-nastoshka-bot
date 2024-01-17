# Itemlist Wikidata Completer

This bot looks for pages in the category [Itemlist with compilation errors](https://it.wikivoyage.org/wiki/Categoria:Itemlist_con_errori_di_compilazione)
explicitely for missing or empty wikidata params and tries to find it in a number of ways:


- By looking at the wikidata label for the item in Italian and English
- By looking at the same item linked in other linguistic versions of wikivoyage (to be done)


## Usage

Have a look at the general setup in the [Usage section](../../../README.md#usage) and 
[Scripts section](../../../README.md#scripts---wip) of the main README.md file.

Then run the script as a normal pywikibot script:

```bash
# minimal (runs for all files in the category)
pwb itemlist_wikidata_completer

## With limit
pwb itemlist_wikidata_completer -limit:1
 
 ## Target another category
pwb itemlist_wikidata_completer -cat:"Itemlist with compilation errors"

## Dry-run (no changes are made)
pwb itemlist_wikidata_completer -simulate
```