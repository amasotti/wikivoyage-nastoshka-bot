import argparse

from bot.wikivoyage import run_citylist_wikidata_check, list_empty_daSapere, sort_template_params


def main(args):
    # Run the script
    if args.script == "citylist-checker":
        run_citylist_wikidata_check(args.lang, int(args.total))
    elif args.script == "empty-da-sapere":
        list_empty_daSapere(args.lang)
    elif args.script == "sort-template":
        page = args.target_page
        template = args.target_template

        if page is None or template is None:
            raise ValueError("You must specify both --target-page and --target-template")
        sort_template_params(page,template, args.lang)
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
    parser.add_argument('--target-page', help='The target page for the script', required=False, default=None)
    parser.add_argument('--target-template', help='The name of the template to sort', required=False, default=None)
    args = parser.parse_args()

    main(args)
