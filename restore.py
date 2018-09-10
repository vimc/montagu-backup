#!/usr/bin/env python3
import sys
from subprocess import run

from settings import load_settings, shared_args

if __name__ == "__main__":
    settings = load_settings()

    for target in settings.targets:
        print("*" * 79)
        print(target.id)
        print("- Doing pre-restore step")
        target.before_restore()
        print("- Beginning restore")
        cmd = ["duplicati-cli", "restore", "--overwrite=true", target.remote_url]
        cmd += sys.argv[1:]
        cmd += shared_args(settings, target.encrypted)
        run(cmd)

        print("- Doing post-restore step")
        target.after_restore()
