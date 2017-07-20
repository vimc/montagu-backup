#!/usr/bin/env python3
from os.path import isfile

from settings import config_path, root_path, load_settings, save_secrets

if __name__ == "__main__":
    if not isfile(config_path):
        print("Missing config files in {}. First copy files from configs/".format(root_path))
        print("For example, for setting up backups on the support machine:")
        print("mkdir -p {0} && cp configs/support.montagu/* {0}".format(root_path))
        exit(-1)

    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    settings = load_settings()
    save_secrets(settings.encrypted)
