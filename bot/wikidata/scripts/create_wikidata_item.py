import json
from typing import Any, Iterable

import pywikibot
from pywikibot import logging
from pywikibot import ItemPage


class WdItem:
    def __init__(self, label, description, claims):
        self.labels = {"en": label}
        self.descriptions = {"en": description}
        self.claims = claims


class WikidataDestinationImporter:

    def __init__(self, items: list[WdItem], **kwargs: Any) -> None:
        self.items = items
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.repo = self.site.data_repository()
        self.itVoyQ = pywikibot.ItemPage(self.site, "Q24237997")
        # self.itVoyQ = pywikibot.ItemPage(self.site, 'Q2459')

    @property
    def edit_opts(self) -> dict[str, Any]:
        return {"summary": "Imported from it.wikivoyage", "watch": "watch"}

    @property
    def generator(self) -> Iterable[WdItem]:
        for item in self.items:
            yield item

    def create_items(self):
        for item in self.generator:
            print(item)
            new_item = pywikibot.ItemPage(self.repo)
            id = new_item.editLabels(item["labels"], summary="Setting label")
            new_item.editDescriptions(
                item["descriptions"], summary="Setting description"
            )

            claims = item["claims"]

            new_item = self.handle_coords(new_item, claims)
            new_item = self.handle_country(new_item, claims)
            new_item = self.handle_instance_of(new_item, claims)
            new_item = self.handle_administrative_entity(new_item, claims)
            self.handle_body_of_water(new_item, claims)

            logging.log("Created item %s with label %s", id, item["labels"]["en"])
            # print(f"Created item {id} with label {item['labels']['en']}")

    def handle_coords(self, item: ItemPage, data):
        lat = data["coords"]["target"]["latitude"]
        lon = data["coords"]["target"]["longitude"]
        coords = pywikibot.Coordinate(
            lat=lat, lon=lon, precision=0.0001, site=self.repo
        )

        claim = pywikibot.Claim(self.repo, "P625")

        claim.setTarget(coords)
        item.addClaim(claim, summary="Adding coordinates")
        return item

    def set_qualifier(self):
        imported_from = pywikibot.Claim(self.repo, "P143")
        imported_from.setTarget(self.itVoyQ)
        return imported_from

    def handle_country(self, item: ItemPage, claims):
        claim = pywikibot.Claim(self.repo, "P17")
        claim.setTarget(pywikibot.ItemPage(self.repo, claims["country"]["target"]))
        claim.addSource(self.set_qualifier())

        item.addClaim(claim, summary="Adding country")
        return item

    def handle_instance_of(self, item: ItemPage, claims: dict):
        claim = pywikibot.Claim(self.repo, "P31")
        instance = claims["instance_of"]["target"]
        claim.setTarget(pywikibot.ItemPage(self.repo, instance))
        claim.addSource(self.set_qualifier())
        item.addClaim(claim, summary="Adding instance of")
        return item

    def handle_administrative_entity(self, item: ItemPage, claims: dict):
        claim = pywikibot.Claim(self.repo, "P131")
        claim.setTarget(
            pywikibot.ItemPage(self.repo, claims["administrative_entity"]["target"])
        )
        claim.addSource(self.set_qualifier())
        item.addClaim(claim, summary="Adding administrative entity")
        return item

    def handle_body_of_water(self, item: ItemPage, claims: dict):
        claim = pywikibot.Claim(self.repo, "P206")
        claim.setTarget(
            pywikibot.ItemPage(self.repo, claims["body_of_water"]["target"])
        )
        claim.addSource(self.set_qualifier())
        item.addClaim(claim, summary="Adding body of water")
        return item


def shared_claims():
    return {
        "country": {
            "property": "P17",
            "target": "Q145",  # UK
        },
        "instance_of": {
            "property": "P31",
            "target": "Q11959973",  # beach
        },
        "administrative_entity": {
            "property": "P131",
            "target": "Q46395",  # British overseas territory
        },
        "body_of_water": {
            "property": "P206",
            "target": "Q1247",  # Caraibbean Sea
        },
    }


def main():
    items = json.load(
        open("bot/wikidata/scripts/item.example.json", "r", encoding="utf-8")
    )

    # Merge the claims in each items['claims'] with the shared claims, if not already present
    for item in items:
        for key, value in shared_claims().items():
            if key not in item["claims"]:
                item["claims"][key] = value

    bot = WikidataDestinationImporter(items)
    bot.create_items()


if __name__ == "__main__":
    main()
