from WikibaseHelper import WikibaseHelper


def main():
    wbase = WikibaseHelper()

    query = """
    SELECT ?item ?itemLabel (COUNT(DISTINCT ?languagelink) AS ?linkcount) WHERE {
  ?item wdt:P31 wd:Q515 .
  ?languagelink schema:about ?item.
  FILTER(NOT EXISTS {
    ?enlanguagelink schema:about ?item;
      schema:inLanguage "it";
      schema:isPartOf <https://it.wikivoyage.org/>.
  })
  SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
}
GROUP BY ?item ?itemLabel
ORDER BY DESC (?linkcount)
LIMIT 20
    """

    gen = wbase.run_query(query)

    for page in gen:
        print(page.title())


if __name__ == "__main__":
    main()
