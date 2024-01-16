from bot.wikidata import WikidataBot

def get_decimal_coords_from_wd_entity(entity:str, target_format:str):
    """
    Get the decimal coordinates from a Wikidata entity.
    """

    wd_bot = WikidataBot()
    coords = wd_bot.get_lat_long(entity)

    if target_format == "wikivoyage":
        return f"| lat= {coords[0]} | long = {coords[1]}"
    else:
        return coords

