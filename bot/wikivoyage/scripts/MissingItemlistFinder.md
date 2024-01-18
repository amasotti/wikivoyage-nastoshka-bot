# Missing Itemlist Finder

Itemlist is a cover term for the templates `{{Città}}` and `{{Destinazione}}` usually used in 
Wikivoyage articles to list the main cities and destinations of a region through the use of
`{{Citylist}}` and `{{Destinationlist}}` templates.

This script finds articles from a given category (usually `Region` or `State`) that
lack a list of cities or destinations, despite of referring to larger entities (states, regions).

## Usage

Have a look at the general setup in the  [README.md](../../../README.md) file.

### Setup 
The script needs two additional parameters; default values are available
but can be overridden if passed via command line:

- `-addcat`: the name of the category to be used for categorization (default: "_Regioni senza Citylist o Destinationlist_")
- `-action`: the action to be performed, one of the following:
  - `add-dump`: finds the articles in the target category and dumps them in a file
  - `add-cat`: finds the articles in the target category and adds them to the service category
  - `remove-dump`: finds the articles in the service category that now have a list of cities or destinations and dumps them in a file
  - `remove-cat`: finds the articles in the service category that now have a list of cities or destinations and removes them from the service category

As you can see from the ´action` parameter, this bot can run in two directions:
- Search for articles in the target category and add them to the service category if the condition is met
- Search for articles in the service category and remove them from the service category if the condition is not met anymore

Of course all global params also apply. Particularly important here is:

- `-cat` (or `-catr` for the recursive version) to specify the category to use for the search

### Run

* **Minimal**: runs for all files in the category. Per default we dump, not modify the articles

```bash
# If you didn't install pywikibot via `pip´, 
# you need to run it with `python pwb.py` instead of just  `pwb`
pwb missing_itemlist_finder

# the same as:
pwb missing_itemlist_finder -addcat:"Regioni senza Citylist o Destinationlist" -action:add-dump

```

* **With limit**: runs for the first 10 files in the category, see generator parameters for more options
like `start`, `namespace`, `cat` and so on
```bash
pwb missing_itemlist_finder -limit:10
```

* **Set target service category**: 
```bash
pwb missing_itemlist_finder -addcat:"Regioni senza Citylist o Destinationlist" -action:add-cat
```

* **Remove from service category**: 
```bash
pwb missing_itemlist_finder -addcat:"Regioni senza Citylist o Destinationlist" -action:remove-cat
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb missing_itemlist_finder -simulate
```