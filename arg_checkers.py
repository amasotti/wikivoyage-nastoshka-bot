
# --------------------  CHECKERS -------------------- #

def check_template_specified(args):
    """
    Checks if both `--target-page` and `--target-template` were specified.
    :param args: The command line arguments object.
    :type args: object
    :raises ValueError: If either `--target-page` or `--target-template` is not specified.
    """
    if args.target_page is None or args.target_template is None:
        raise ValueError("You must specify both --target-page and --target-template")


def check_target_entity_specified(args):
    """
    Checks if both `--target-page` and `--target-template` were specified.
    :param args: The command line arguments object.
    :type args: object
    :raises ValueError: If either `--target-page` or `--target-template` is not specified.
    """
    if args.target_entity is None:
        raise ValueError("You must specify --target-entity")