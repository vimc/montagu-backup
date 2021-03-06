#!/usr/bin/env python3
import logging
from datetime import date
from os import makedirs
from os.path import join, isdir
from subprocess import Popen, PIPE

from settings import load_settings, shared_args, log_dir
from helpers import flatten


def ensure_dir_exists(dir_path):
    if not isdir(dir_path):
        makedirs(dir_path)


def with_logging(do):
    ensure_dir_exists(log_dir)
    # Log everything to a rotating file
    filename = join(log_dir, "duplicati_{}.log".format(date.today().isoformat()))
    log_format = "%(asctime)s    %(levelname)s    %(message)s"
    logging.basicConfig(filename=filename, level=logging.DEBUG, format=log_format)
    logging.info("*" * 60)
    # Also log info and higher messages to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s    %(message)s'))
    logging.getLogger('').addHandler(console)
    try:
        do()
    except Exception as e:
        logging.error("An error occurred:", exc_info=e)
        exit(-1)


def run_duplicati(target, settings):
    cmd = ["duplicati-cli", "backup", target.remote_url]
    cmd += target.paths
    cmd += shared_args(settings, target.encrypted)
    if target.max_versions:
        cmd += ["--keep-versions={}".format(target.max_versions)]
        logging.info("Keeping the {} most recent remote versions".format(
            target.max_versions))

    with Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            logging.info(line.strip())
        for line in p.stderr:
            logging.error(line.strip())

    if p.returncode not in [0, 1]:
        raise Exception("Duplicati backup process for {target} returned error "
                        "code {code}".format(target=target.id,
                                             code=p.returncode))


def run():
    settings = load_settings()
    logging.info("Beginning backup run for these targets: ")
    for target in settings.targets:
        logging.info(" - " + target.id)

    for target in settings.targets:
        logging.info("\n" + ("*" * 79))
        logging.info(target.id)
        logging.info("- Doing pre-backup step")
        target.before_backup()
        logging.info("- About to backup {paths} to {bucket}".format(
            paths=target.paths, bucket=target.bucket))
        run_duplicati(target, settings)


if __name__ == "__main__":
    print("Running backup. Output will be logged to " + log_dir)
    with_logging(run)
