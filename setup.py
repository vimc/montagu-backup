#!/usr/bin/env python3
from os.path import isfile

from settings import config_path, root_path, load_settings, save_secrets

if __name__ == "__main__":
    if not isfile(config_path):
        print("Expecting a file at " + config_path)
        print("Missing config file. First copy file from configs/".format(root_path))
        print("For example, for setting up backups on the annex machine:")
        print("cp configs/annex.json config.json")
        exit(-1)

    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    settings = load_settings()
    save_secrets(any(t for t in settings.targets if t.encrypted))
