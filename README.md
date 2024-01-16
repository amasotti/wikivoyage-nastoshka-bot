# Wikivoyage Nastoshka Bot

Small Python utility based on `pywikibot` for routine tasks on [Wikivoyage](https://it.wikivoyage.org/).


## Features
At moment the only feature I'm working on is the `citylist` template updater.

- `citylist template updater`: check the usages of `{{citylist}}` template with missing `wikidata` param, 
retrieve the missing data from Wikidata and update the page.
- `empty-da-sapere`: check the pages with empty "Da sapere" section and lists these pages in a report logfile.
- `sort-template`: sort the params of a template in a page. Useful for `{{Citylist}}` template, where moving the
different params is cumbersome. This script needs (to be improved and...) two additional params:
    - `--target-page`: the page where the template is located and where the sorting will be applied
    - `--target-template`: the name of the template to be sorted

### Utilities
*because I'm lazy...*

- `get-coordinates`: Retrieves the coordinates of a place from Wikidata and prints them in a format ready to be pasted
in a listing template. This script needs (to be improved and...) two additional params:
    - `--target-entity`: the name of the entity to be searched on Wikidata (e.g. Q123456)


## Usage

1. Clone the repo
1. Install [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot)
2. Generate a user-config.py file with `pwb generate_user_files`
3. Login with `pwb login`
4. Run the script 
   - `python main.py -s citylist-checker -t 2` for the `citylist` template updater
   - `python main.py -s empty-da-sapere` for the empty "Da sapere" section checker
   - `python main.py -s sort-template --target-page "Alpi sveve" --target-template Citylist`
   - `python main.py -s get-coordinates --target-entity Q1969097`

## License
see [LICENSE](LICENSE) file


## About me

You can find me on [Wikivoyage](https://it.wikivoyage.org/wiki/Utente:Nastoshka), 
[Wikipedia](https://it.wikipedia.org/wiki/Utente:Nastoshka) or [Meta](https://meta.wikimedia.org/wiki/User:Nastoshka)