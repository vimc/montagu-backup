#!/usr/bin/env python3
from os.path import abspath, dirname, join, isfile

import sys
from crontab import CronTab

from settings import log_dir

tab_path = "/etc/cron.d/montagu"


def clear_existing(cron, backup_script):
    existing = cron.find_command(backup_script)
    for job in existing:
        cron.remove(job)


def add_job(cron, backup_script, test_job):
    job = cron.new(command=backup_script, comment="Duplicati backup", user="root")
    job.day.every(1)
    job.hour.on(2)
    job.minute.on(0)
    if test_job:
        print("Running scheduled job now as a test. Output will be logged to " + log_dir)
        job.run()


def schedule_backups(test_job):
    here = dirname(abspath(__file__))
    print("Scheduling backup task")
    backup_script = join(here, "backup.py")
    if isfile(tab_path):
        cron = CronTab(tabfile=tab_path, user=False)
    else:
        cron = CronTab()
    clear_existing(cron, backup_script)
    add_job(cron, backup_script, test_job)
    cron.write(tab_path)

    print("Completed scheduling")

if __name__ == "__main__":
    test_job = True
    if len(sys.argv) > 0 and sys.argv[1] == "--no-immediate-backup":
        test_job = False
    schedule_backups(test_job)
