from arg_checkers import *  # Funcs to check that the right arguments are specified
from bot.wikivoyage.scripts import *  # WIKIVOYAGE SCRIPTS


# --------------------  RUNNERS -------------------- #
def check_and_run_sort_template(args):
    """
    :param args: The command line arguments passed to the method.
    :return: None

    This method checks if the necessary template parameters are specified in the command
    line arguments and calls the sort_template_params method accordingly.
    """
    check_template_specified(args)
    sort_template_params(args.target_page, args.target_template, args.lang)


def check_and_run_fix_empty_dynamicMap(args):
    """
    :param args: The command line arguments passed to the method.
    :return: None

    This method checks if the necessary template parameters are specified in the command
    line arguments and calls the sort_template_params method accordingly.
    """
    check_coords_dynamic_maps(args.lang, args.total)


# --------------------  SCRIPT DISPATCH TABLE -------------------- #

SCRIPT_DISPATCH_TABLE = {
    "sort-template": check_and_run_sort_template,
    "fix-empty-dynamicMap": check_and_run_fix_empty_dynamicMap,
}


def run(args):
    print("Checking for script" + args.script)
    script_function = SCRIPT_DISPATCH_TABLE.get(args.script)

    if script_function is None:
        raise ValueError(f"Unknown script: {args.script}")

    script_function(args)
