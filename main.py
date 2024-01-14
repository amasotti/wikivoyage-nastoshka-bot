import argparse

from bot.wikivoyage import run_citylist_wikidata_check


def main(args):
    # Run the script
    if args.script == "citylist-checker":
        run_citylist_wikidata_check(args.lang, int(args.total))
    else:
        raise ValueError(f"Unknown script: {args.script}")


def list_scripts():
    print("citylist-checker : Check the citylist for wikidata ids")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the wikivoyage Nastoshka bot',
        usage='main.py -s <script> [-l <lang> -t <total>]\navailable scripts:\n'+
              '\tcitylist-checker : Check the citylist for wikidata ids'
    )
    parser.add_argument('-s', '--script', help='Run a specific script', required=False)
    parser.add_argument('-l', '--lang', help='The language to use', required=False, default='it')
    parser.add_argument('-t', '--total', help='The total number of articles to check', required=False, default=1)
    args = parser.parse_args()

    main(args)
