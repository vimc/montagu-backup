#!/usr/bin/env bash
# Returns 0 if no setup is needed, or 1 if setup is needed

ALREADY_SETUP=0
NEEDS_SETUP=1

dpkg -s duplicati   || exit NEEDS_SETUP
dpkg -s python3-pip || exit NEEDS_SETUP
[[ ! -f /etc/montagu/backup/config.json  ]] || exit NEEDS_SETUP
[[ ! -f /etc/montagu/backup/secrets.json ]] || exit NEEDS_SETUP

exit ALREADY_SETUP