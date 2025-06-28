# Complete Table Best Image

This bot processes HTML tables on Wikivoyage pages, specifically designed to enhance tables containing destination/location information. 
The script extracts marker templates from table cells, retrieves their Wikidata IDs, and enhances them with:

- **Best images** from Wikidata using the `{{getBestImage}}` template
- **Coordinates** (latitude/longitude) from Wikidata  
- **Wikidata IDs** for proper data linking

The bot is particularly useful for tables listing places, cities, or destinations where you want to automatically add representative images and geographic coordinates.

## How it Works

1. **Table Detection**: Scans pages for HTML `<table>` elements
2. **Row Processing**: Processes each table row (skipping headers) that contains exactly 4 cells
3. **City Name Extraction**: Extracts city/location names from `{{marker}}` templates in table cells
4. **Wikidata Lookup**: Attempts to find corresponding Wikidata entities for each location
5. **Content Enhancement**: 
   - Adds `{{getBestImage}}` template with Wikidata ID to display optimal images
   - Enriches marker templates with Wikidata IDs and coordinates
   - Updates table cells with enhanced content

## Table Structure Expected

The bot expects tables with 4 columns where:
- **Column 1**: Will be populated with `{{getBestImage}}` template  
- **Column 2**: Contains `{{marker}}` templates with location information
- **Columns 3-4**: Additional data (state, year, description, etc.)

## Usage

Have a look at the general setup in the [Usage section](../../../README.md#usage) and 
[Scripts section](../../../README.md#scripts) of the main README.md file.

Then run the script as a normal pywikibot script:

* **Minimal**: runs for specified pages
```bash
# If you didn't install pywikibot via `pip`, 
# you need to run it with `python pwb.py` instead of just `pwb`
pwb complete_table_best_image -page:"PageTitle"
```

* **Multiple pages**: process several pages at once
```bash
pwb complete_table_best_image -page:"Page1" -page:"Page2" -page:"Page3"
```

* **With category**: runs for all pages in a category
```bash
pwb complete_table_best_image -cat:"CategoryName"
```

* **With limit**: process only the first N pages
```bash
pwb complete_table_best_image -cat:"CategoryName" -limit:5
```

* **Dry-run**: no changes are made, just a simulation
```bash
pwb complete_table_best_image -page:"PageTitle" -simulate
```

## Interactive Mode

When the bot cannot automatically find a Wikidata ID for a location, it will prompt you interactively:

```
Enter wikidata id for LocationName: Q123456
```

Enter the correct Wikidata ID (e.g., `Q123456`) or press Enter to skip.

## Output

The script generates a file called `pueblos_magicos.txt` containing the processed wikicode for review before applying changes to live pages.

## Example Transformation

**Before:**
```wikitext
{| class="wikitable"
! Image !! Location !! State !! Year
|-
| || {{marker|nome=[[Example City]]|lat= |long=}} || Example State || 2020
|}
```

**After:**
```wikitext
{| class="wikitable"  
! Image !! Location !! State !! Year
|-
| {{getBestImage|Q123456|300px}} || {{marker|nome=[[Example City]]|lat=12.3456 |long=-98.7654|wikidata=Q123456}} || Example State || 2020
|}
```

## Dependencies

- **WikibaseHelper**: For Wikidata entity lookups and coordinate retrieval
- **mwparserfromhell**: For parsing and manipulating wikitext
- **pywikibot**: Core MediaWiki bot framework

## Notes

- The script is currently configured for Italian Wikivoyage ("it" language)
- It expects specific table structures with marker templates
- Manual input may be required for locations not found automatically in Wikidata
- Always review the generated output file before applying changes to live pages