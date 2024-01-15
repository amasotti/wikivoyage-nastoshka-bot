import argparse

from bot.wikivoyage import run_citylist_wikidata_check, list_empty_daSapere, sort_template_params


def main(args):
    script_dispatch_table = {
        "citylist-checker": (run_citylist_wikidata_check, 2),
        "empty-da-sapere": (list_empty_daSapere, 1),
        "sort-template": (check_template_specified, 1, sort_template_params, 3),
    }

    script_info = script_dispatch_table.get(args.script)
    if script_info is None:
        raise ValueError(f"Unknown script: {args.script}")

    # Check the number of arguments
    if len(script_info) == 2:
        script, num_params = script_info
        if num_params == 1:
            script(args.lang)
        elif num_params == 2:
            script(args.lang, int(args.total))
    else:
        script, num_params, actual_script, actual_num_params = script_info
        script(args)
        if actual_num_params == 3:
            actual_script(args.target_page, args.target_template, args.lang)

def check_template_specified(args):
    """
    Checks if both `--target-page` and `--target-template` were specified.

    :param args: The command line arguments object.
    :type args: object

    :raises ValueError: If either `--target-page` or `--target-template` is not specified.
    """
    if args.target_page is None or args.target_template is None:
        raise ValueError("You must specify both --target-page and --target-template")


def list_scripts():
    """
    Print the script names.

    :return: None
    """
    print("citylist-checker : Check the citylist for wikidata ids")
    print("empty-da-sapere : Check for empty 'Da sapere' sections")
    print("sort-template : Sort the parameters of a template")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the wikivoyage Nastoshka bot',
        usage='main.py -s <script> [-l <lang> -t <total>]\navailable scripts:\n' +
              '\tcitylist-checker : Check the citylist for wikidata ids'
    )
    parser.add_argument('-s', '--script', help='Run a specific script', required=False)
    parser.add_argument('-l', '--lang', help='The language to use', required=False, default='it')
    parser.add_argument('-t', '--total', help='The total number of articles to check', required=False, default=1)
    parser.add_argument('--target-page', help='The target page for the script', required=False, default=None)
    parser.add_argument('--target-template', help='The name of the template to sort', required=False, default=None)
    args = parser.parse_args()

    main(args)
