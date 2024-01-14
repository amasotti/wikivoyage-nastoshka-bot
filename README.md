# Wikivoyage Nastoshka Bot

Small Python utility based on `pywikibot` for routine tasks on [Wikivoyage](https://it.wikivoyage.org/).


## Features
At moment the only feature I'm working on is the `citylist` template updater.

- `citylist template updater`: check the usages of `{{citylist}}` template with missing `wikidata` param, 
retrieve the missing data from Wikidata and update the page.


## Usage

1. Clone the repo
1. Install [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot)
2. Generate a user-config.py file with `pwb generate_user_files`
3. Login with `pwb login`
4. Run the script 

## License
see [LICENSE](LICENSE) file


## About me

You can find me on [Wikivoyage](https://it.wikivoyage.org/wiki/Utente:Nastoshka), 
[Wikipedia](https://it.wikipedia.org/wiki/Utente:Nastoshka) or [Meta](https://meta.wikimedia.org/wiki/User:Nastoshka)