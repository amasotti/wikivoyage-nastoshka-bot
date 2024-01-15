from bot.wikivoyage import citylist_wikidata_check, list_empty_daSapere, sort_template_params


def check_and_run_citylist_checker(args):
    """
    :param args: a dictionary containing the following information:
        - lang: a string representing the language code
        - total: an integer representing the total number of cities to check
    :return: None

    This method checks and runs the citylist_checker for the specified language and total number of cities.
    """
    citylist_wikidata_check(args.lang, int(args.total))


def check_and_run_empty_da_sapere(args):
    """
    Check and run the empty_da_sapere function.

    :param args: The arguments for the function.
    :return: None
    """
    list_empty_daSapere(args.lang)


def check_and_run_sort_template(args):
    """
    :param args: The command line arguments passed to the method.
    :return: None

    This method checks if the necessary template parameters are specified in the command
    line arguments and calls the sort_template_params method accordingly.
    """
    check_template_specified(args)
    sort_template_params(args.target_page, args.target_template, args.lang)


SCRIPT_DISPATCH_TABLE = {
    "citylist-checker": check_and_run_citylist_checker,
    "empty-da-sapere": check_and_run_empty_da_sapere,
    "sort-template": check_and_run_sort_template,
}


def run(args):
    print("Checking for script" + args.script)
    script_function = SCRIPT_DISPATCH_TABLE.get(args.script)

    if script_function is None:
        raise ValueError(f"Unknown script: {args.script}")

    script_function(args)


def check_template_specified(args):
    """
    Checks if both `--target-page` and `--target-template` were specified.
    :param args: The command line arguments object.
    :type args: object
    :raises ValueError: If either `--target-page` or `--target-template` is not specified.
    """
    if args.target_page is None or args.target_template is None:
        raise ValueError("You must specify both --target-page and --target-template")
