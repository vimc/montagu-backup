#!/usr/bin/env python3
"""
Duplicati CLI wrapper

Usage:
  cli.py TARGET TASK [ADDITIONAL_ARGS ...]
  cli.py list-targets

Where:
  TARGET is the id of a target in the current config
  TASK is a duplicati-cli task (see https://duplicati.readthedocs.io/en/latest/04-using-duplicati-from-the-command-line/)
  and any additional arguments are passed to duplicati-cli
"""

from subprocess import run

from docopt import docopt

from settings import load_settings, shared_args


def run_task(options, settings):
    target = next(t for t in settings.targets if t.id == options["TARGET"])
    cmd = ["duplicati-cli", options["TASK"], target.remote_url]
    cmd += options["ADDITIONAL_ARGS"]
    cmd += shared_args(settings, target.encrypted)
    run(cmd)


if __name__ == "__main__":
    options = docopt(__doc__)
    settings = load_settings()
    if options["list-targets"]:
        for target in settings.targets:
            print(target.id)
    else:
        run_task(options, settings)
