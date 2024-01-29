# Template_x_Cat

On wikivoyage some templates are expected (or never expected) to be used in articles with a certain category. This script checks for such cases and reports them.
It can works with two modes:
- Checking that an article using a given template is in a given category
- Checking that an article using a given template is __not__ in a given category

## Usage

Have a look at the general setup in the  [README.md](../../../README.md) file.

### Setup 
The script needs just the name of the old code to be replaced (the new one is retrieved from Wikidata):

- `targetcat`: (__required__) the category to be checked
- `negative`: if set the script checks that the article is __not__ in the category, default is `False`
- `format`: the format of the output file. Can be one of `wikitext`, `json`, or `plaintext`. Default is `wikitext`
- `outputfile`: the path or name of the output file. Default is `template_x_cat_result.txt`

The script also requires the name of the template to be checked, given with the pwb standard param `-transcludes:"templateName"`    

### Run

```bash
# If you didn't install pywikibot via `pip´, 
# you need to run it with `python pwb.py` instead of just  `pwb`
pwb template_x_cat -targetcat:"Regioni" -transcludes:"Template:QuickbarCity"
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb template_x_cat -targetcat:"Regioni" -transcludes:"Template:QuickbarCity" -simulate
```