# Get Coordinates for Listing

This is less a bot and more a utility script for lazy people like me :)
We often have to enter `lat`, `long` and `wikidata` in the `listing` template (
see, do, buy, eat, drink, sleep, città etc..) and copying and pasting from Wikidata
or from other sources is cumbersome. This script does it for you, printing the 
string ready to be pasted in the listing template.


## Usage

see general setup in the [README.md](../../../README.md) file.
Since this is a wikidata "bot", you'll need to add the folder in the `user-config.py` file

### Run

* **Minimal**: runs for all files in the category. Per default we dump, not modify the articles

```bash
pwb get_wikivoyage_coordinates -item:Q3033
```

will output:

```
| lat= 51.5339 | long= 9.93556 | wikidata= Q3033
```
