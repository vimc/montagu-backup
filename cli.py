#!/usr/bin/env python3
from subprocess import run

import sys

from settings import load_settings, shared_args

usage = """Usage:
./cli.py TARGET TASK ...
where:
  TARGET is the id of a target in the current config
  TASK is a duplicati-cli task (see https://duplicati.readthedocs.io/en/latest/04-using-duplicati-from-the-command-line/)
  and ... is any additional arguments to pass to duplicati-cli"""

if __name__ == "__main__":
    settings = load_settings()
    if len(sys.argv) < 3:
        print(usage)
        exit(1)
        
    target = next(t for t in settings.targets if t.id == sys.argv[1])
    task = sys.argv[2]
    cmd = ["duplicati-cli", task, target.remote_url]
    if len(sys.argv) > 3:
        cmd += sys.argv[3:]
    cmd += shared_args(settings, target.encrypted)
    run(cmd)
