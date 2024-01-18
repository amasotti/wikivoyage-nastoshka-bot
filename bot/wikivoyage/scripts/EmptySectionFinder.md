# Empty Section Finder

This script finds articles with a given section being emtpy and either categorizes them or 
dumps a list of them to be checked manually.

## Usage

Have a look at the general setup in the  [README.md](../../../README.md) file.

### Setup 
The script needs three additional parameters; default values are available
but can be overridden if passed via command line:

- `-section`: the name of the section to be checked (default: "_Da sapere_")
- `-addcat`: the name of the category to be used for categorization (default: "_Articoli senza introduzione_")
- `-action`: the action to be performed, either `addcat` for categorization or `dump` for dumping a list of articles (default: `dump`)

Of course all global params also apply. Particularly important here is:

- `-cat` (or `-catr` for the recursive version) to specify the category to use for the search

### Run

* **Minimal**: runs for all files in the category
```bash
# If you didn't install pywikibot via `pip´, 
# you need to run it with `python pwb.py` instead of just  `pwb`
pwb empty_section_finder

# the same as:
pwb empty_section_finder -section:"Da sapere" -addcat:"Articoli senza introduzione" -action:dump
```

* **With limit**: runs for the first 10 files in the category, see generator parameters for more options
like `start`, `namespace`, `cat` and so on
```bash
pwb empty_section_finder -limit:10
```

* **Search in a particular category**: runs for all files in the category
```bash
pwb empty_section_finder -cat:"Articoli senza introduzione"
```

* **Set target service category**: 
```bash
pwb empty_section_finder -addcat:"Articoli senza introduzione"
```

* **Categorize**: categorizes the articles in the target category
```bash
pwb empty_section_finder -action:addcat
```

* **Dump**: dumps a list of articles in the target category
```bash
pwb empty_section_finder -action:dump
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb itemlist_wikidata_completer -simulate
```