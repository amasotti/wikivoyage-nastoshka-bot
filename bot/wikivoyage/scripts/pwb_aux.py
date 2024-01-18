from typing import Iterable, Any

from pywikibot import pagegenerators


def setup_generator(local_args: list[str]) -> tuple[Iterable | None, dict[str, Any]]:
    options = {}
    gen_factory = pagegenerators.GeneratorFactory()
    for arg in gen_factory.handle_args(local_args):
        if arg.startswith('-'):
            arg, sep, value = arg.partition(':')
            if value != '':
                options[arg[1:]] = value if not value.isdigit() else int(value)
            else:
                options[arg[1:]] = True
    generator = gen_factory.getCombinedGenerator()
    return generator, options
