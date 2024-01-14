import argparse

from bot.wikivoyage import run_citylist_wikidata_check


def main(args):
    # Docs
    if args.list_scripts:
        list_scripts()
        exit(0)

    # Run the script
    if args.script == "citylist.checker":
        run_citylist_wikidata_check()
    else:
        raise ValueError(f"Unknown script: {args.script}")


def list_scripts():
    print("citylist-checker : Check the citylist for wikidata ids")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the wikivoyage Nastoshka bot')
    parser.add_argument('-s', '--script', help='Run a specific script', required=False)
    parser.add_argument('-l', '--list-scripts', help='List available scripts', action='store_true')
    args = parser.parse_args()

    main(args)
