import pywikibot

COORDINATES_PROPERTY = 'P625'


class EntityCoordinateGetter(object):

    def __init__(self, item):
        self.site = pywikibot.Site().data_repository()
        self.item = item

    @staticmethod
    def _truncate_coordinates(coords):
        return tuple(format(x, '.6g') for x in coords)

    def get_lat_long(self):
        """
        Get the latitude and longitude of a given wikidata item
        :param wikidata_item:
        :return:
        """
        item = pywikibot.ItemPage(site=self.site, title=self.item)
        item_dict = item.get()
        claims = item_dict["claims"]
        coords = (None, None)
        if COORDINATES_PROPERTY in claims:
            for claim in claims[COORDINATES_PROPERTY]:
                coords = claim.getTarget().lat, claim.getTarget().lon

                # Preserve only 6 digits in total for lat and long
                coords = self._truncate_coordinates(coords)
        return coords

    def run(self):
        coords = self.get_lat_long()
        voy_str = f"| lat= {coords[0]} | long= {coords[1]} | wikidata= {self.item}"
        print(voy_str)


#   def build_query(args: list[str]):
#
#     item_param = [arg for arg in args if arg.startswith("-item:")][0]
#
#     if not item_param:
#         raise ValueError("No item given")
#
#     entity = item_param.split(":")[1]
#
#     query = """
#     SELECT ?item ?entityLabel ?lat ?long WHERE {
#   wd:%(entity) p:P625 ?statement .
#   ?statement psv:P625 ?coordinate_node .
#   ?coordinate_node wikibase:geoLatitude ?lat .
#   ?coordinate_node wikibase:geoLongitude ?long .
#
#   SERVICE wikibase:label {
#     bd:serviceParam wikibase:language "it" .
#   }
#   BIND(wd:%(entity) AS ?entity)
# }
# """
#
#     query = query.replace("%(entity)", entity)
#     return query

def get_wikidata_item_from_args(args):
    item_param = [arg for arg in args if arg.startswith("-item:")][0]

    if not item_param:
        raise ValueError("No item given")

    entity = item_param.split(":")[1]

    return entity


def main():
    args = pywikibot.handle_args()
    item = get_wikidata_item_from_args(args)

    bot = EntityCoordinateGetter(item=item)
    bot.run()


if __name__ == '__main__':
    main()
