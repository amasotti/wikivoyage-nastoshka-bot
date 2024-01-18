# Update Mapcode Quickbar

This is a small pwb script that updates the mapcode in the `{{`[Quickbar](https://it.wikivoyage.org/wiki/Template:QuickbarCity)`}}` template
## Usage

Have a look at the general setup in the  [README.md](../../../README.md) file.

### Setup 
The script needs just the name of the old code to be replaced (the new one is retrieved from Wikidata):

- `-oldcode`: the old code to be replaced (case is ignored, since the code is normalized to lowercase)Of course all global params also apply. Particularly important here is:

- `-cat` (or `-catr` for the recursive version) to specify the category to use for the search

### Run

* **Minimal**: runs for all files in the category. Per default we dump, not modify the articles

```bash
# If you didn't install pywikibot via `pip´, 
# you need to run it with `python pwb.py` instead of just  `pwb`
pwb update_mapcode_quickbar -oldcode:"uk"
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb update_mapcode_quickbar -oldcode:"uk" -simulate
```