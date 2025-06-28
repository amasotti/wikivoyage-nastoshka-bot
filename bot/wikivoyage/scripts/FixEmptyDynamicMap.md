# Dynamic Map Filler

This script iterates over the articles in a given category (either `Mappa dinamica senza coordinate` or the
one passed via `-cat` parameter) and tries to fix them by adding the missing coordinates
from Wikidata.


## Usage

Have a look at the general setup in the  [README.md](../../../README.md) file.

### Run

* **Minimal**: runs for all files in the category
```bash
# If you didn't install pywikibot via `pip´, 
# you need to run it with `python pwb.py` instead of just  `pwb`
pwb fix_empty_dynamic_map
```

* **With limit**: runs for the first 10 files in the category, see generator parameters for more options
like `start`, `namespace`, `cat` and so on
```bash
pwb fix_empty_dynamic_map -limit:10
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb fix_empty_dynamic_map -simulate
```