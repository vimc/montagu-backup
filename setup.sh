#!/usr/bin/env bash
set -e

file_name=duplicati_2.0.1.73-1_all.deb

apt-get -q install gdebi cron -y
if [ ! -f ${file_name} ]; then
    wget https://updates.duplicati.com/experimental/${file_name}
fi
dpkg -s duplicati 2>/dev/null >/dev/null || gdebi --non-interactive ${file_name}

apt-get install python3-pip -y
pip3 install --quiet -r ${BASH_SOURCE%/*}/requirements.txt

export VAULT_ADDR='https://support.montagu.dide.ic.ac.uk:8200'
if [ "$VAULT_AUTH_GITHUB_TOKEN" = "" ]; then
    echo -n "Please provide your GitHub personal access token for the vault: "
    read -s token
    echo ""
    export VAULT_AUTH_GITHUB_TOKEN=${token}
fi
vault login -method=github

${BASH_SOURCE%/*}/setup.py

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
