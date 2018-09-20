#!/usr/bin/env python3
"""
Duplicati CLI wrapper

Usage:
  cli.py TARGET TASK [-- ADDITIONAL_ARGS]
  cli.py list-targets

Where:
  TARGET is the id of a target in the current config
  TASK is a duplicati-cli task (see https://duplicati.readthedocs.io/en/latest/04-using-duplicati-from-the-command-line/)
  ADDITIONAL ARGS are additional arguments to be passed through to duplicati-cli
"""
import sys
from subprocess import run

from docopt import docopt

from settings import load_settings, shared_args


def run_task(options, additional_args, settings):
    target = next(t for t in settings.targets if t.id == options["TARGET"])
    cmd = ["duplicati-cli", options["TASK"], target.remote_url]
    cmd += additional_args
    cmd += shared_args(settings, target.encrypted)
    run(cmd)


def parse_args():
    args = sys.argv[1:]
    if "--" in args:
        index = args.index("--")
        docopt_args = args[:index]
        additional_args = args[(index + 1):]
    else:
        docopt_args = args
        additional_args = []
    options = docopt(__doc__, argv=docopt_args)
    return options, additional_args


if __name__ == "__main__":
    options, additional_args = parse_args()
    settings = load_settings()
    if options["list-targets"]:
        for target in settings.targets:
            print(target.id)
    else:
        run_task(options, additional_args, settings)
