# Wikivoyage Nastoshka Bot

Small Python utility based on `pywikibot` for routine tasks on [Wikivoyage](https://it.wikivoyage.org/).

It's based on 

- Python v. `3.10`
- Pywikibot v. `10.1.0` (current stable release: [docs](https://doc.wikimedia.org/pywikibot/stable/))

## Usage

1. Clone the repo
2. Install [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot)
3. Generate a user-config.py file with `pwb generate_user_files`
4. Login with `pwb login`
5. Run the script (*see below under "Scripts" for more details*):

## Scripts

- [Itemlist Wikidata Completer](bot/wikivoyage/scripts/ItemlistWikidataCompleter.md) - script to fill the params `wikidata`, `lat`, `long` in Itemlist (Città and Destinazione) that lack them
- [Empty section finder](bot/wikivoyage/scripts/EmptySectionFinder.md) - script to find empty sections in articles given the 
name of the category and of the section to be checked
- [Missing Itemlist Finder](bot/wikivoyage/scripts/MissingItemlistFinder.md) - script to find articles from a given category (usually `Region` or `State`) 
that lack a list of cities or destinations, despite of referring to larger entities (states, regions)
- [DynamicMap Filler](bot/wikivoyage/scripts/FixEmptyDynamicMap.md) - script to fill the `dynamicmap` lat and long parameter in articles that lack it


### Utilities

- [Wikivoyage coordinates getter](bot/wikidata/scripts/GetCoordinatesForWikivoyage.md) - script to get the coordinates for a given Wikidata item
in wikivoyage listing format (lat=, long=, wikidata=)

### Start as a pywikibot script

To start the scripts in this way, add this line to your `user-config.py`:

```python
user_script_paths=["bot/wikivoyage/scripts"] # or the path where you cloned the script
```

Then run as a normal pywikibot script:

```bash
pwb <script-name> <options>
```

## Useful resources

- [Pywikibot sample script](https://doc.wikimedia.org/pywikibot/stable/library_usage.html)
- [Generator Parameters](https://doc.wikimedia.org/pywikibot/stable/api_ref/pywikibot.pagegenerators.html#generator-options)
- [Global Parameters](https://doc.wikimedia.org/pywikibot/stable/global_options.html)

## License
see [LICENSE](LICENSE) file


## About me

You can find me on [Wikivoyage](https://it.wikivoyage.org/wiki/Utente:Nastoshka), 
[Wikipedia](https://it.wikipedia.org/wiki/Utente:Nastoshka) or [Meta](https://meta.wikimedia.org/wiki/User:Nastoshka)