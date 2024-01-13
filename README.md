# Wikivoyage Citylist filler

Small Python utility based on `pywikibot` to fill the Wikivoyage 
check the usages of `{{citylist}}` template with missing `wikidata` param, 
retrieve the missing data from Wikidata and update the page.


## Usage

1. Clone the repo
1. Install [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot)
2. Generate a user-config.py file with `pwb generate_user_files`
3. Login with `pwb login`
4. Run the script 