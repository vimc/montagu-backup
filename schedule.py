#!/usr/bin/env python3
"""
Schedule Duplicati backups.

Usage:
  schedule.py <user> [--hour=<hour>] [--no-immediate-backup]

Options:
  --hour=<hour>          Hour (on 24-hour clock) to run at [default: 2]
  --no-immediate-backup  Do not test the scheduled job

Schedules Duplicati backup to be run daily at the specified hour, as the
specified user. This should probably be "montagu".
"""

from os.path import abspath, dirname, join, isfile

from crontab import CronTab
from docopt import docopt

from settings import log_dir

tab_path = "/etc/cron.d/montagu"


def clear_existing(cron, backup_script):
    existing = cron.find_command(backup_script)
    for job in existing:
        cron.remove(job)


def add_job(cron, backup_script, options):
    job = cron.new(command=backup_script,
                   comment="Duplicati backup",
                   user=options["<user>"])
    job.day.every(1)
    job.hour.on(int(options["--hour"]))
    job.minute.on(0)
    if not options["--no-immediate-backup"]:
        print("Running scheduled job now as a test. Output will be logged to " + log_dir)
        job.run()


def schedule_backups(options):
    here = dirname(abspath(__file__))
    print("Scheduling backup task")
    backup_script = join(here, "backup.py")
    if isfile(tab_path):
        cron = CronTab(tabfile=tab_path, user=False)
    else:
        cron = CronTab(user=False)
    clear_existing(cron, backup_script)
    add_job(cron, backup_script, options)
    cron.write(tab_path)

    print("Completed scheduling")


if __name__ == "__main__":
    options = docopt(__doc__)
    schedule_backups(options)
