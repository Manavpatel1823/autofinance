# Copied from fievel builder and simplified
import argparse
import os


def _get_parser(prog, description, actions):
    # Main parser
    parser = argparse.ArgumentParser(prog=prog, description=description)
    subparsers = parser.add_subparsers(title="sub-commands")

    for action in actions:
        added = action.setup(subparsers)

        added.add_argument(
            "--cwd",
            default=".",
            help="Root directory to run this command at",
        )
        added.set_defaults(__action=action)

    return parser


def _get_args(parser, raw_args):
    args = parser.parse_args(raw_args)
    try:
        action = args.__action
    except AttributeError:
        action = None
        parser.print_help()
        parser.exit()

    abs_cwd = os.path.abspath(args.cwd)
    del args.cwd

    return action, args, abs_cwd


def handle(prog, description, actions, raw_args):
    parser = _get_parser(prog, description, actions)
    action, args, cwd = _get_args(parser, raw_args)

    return action.handle(args, cwd)
