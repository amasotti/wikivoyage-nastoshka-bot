# Itemlist Wikidata Completer

This bot looks for pages in the category [Itemlist with compilation errors](https://it.wikivoyage.org/wiki/Categoria:Itemlist_con_errori_di_compilazione)
explicitely for missing or empty wikidata params and tries to find it in a number of ways:


- By looking at the wikidata label for the item in Italian and English
- By looking at the same item linked in other linguistic versions of wikivoyage (to be done)


## Usage

Have a look at the general setup in the [Usage section](../../../README.md#usage) and 
[Scripts section](../../../README.md#scripts) of the main README.md file.

Then run the script as a normal pywikibot script:

* **Minimal**: runs for all files in the category
```bash
# If you didn't install pywikibot via `pip´, 
# you need to run it with `python pwb.py` instead of just  `pwb`
pwb itemlist_wikidata_completer
```

* **With limit**: runs for the first 10 files in the category, see generator parameters for more options
like `start`, `namespace`, `cat` and so on
```bash
pwb itemlist_wikidata_completer -limit:10
```

* **With target category**: runs for all files in the category `Itemlist with compilation errors`
```bash
pwb itemlist_wikidata_completer -cat:"Itemlist with compilation errors"
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb itemlist_wikidata_completer -simulate
```