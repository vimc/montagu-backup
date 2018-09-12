#!/usr/bin/env bash
set -e

sudo apt-get -q install gdebi cron python3-pip -y

if which -a duplicati-cli > /dev/null; then
    echo "Duplicati is already installed"
else
    echo "installing Duplicati"
    file_name=duplicati_2.0.3.3-1_all.deb
    wget https://updates.duplicati.com/beta/${file_name}
    sudo gdebi --non-interactive ${file_name}
fi

sudo pip3 install --quiet -r ${BASH_SOURCE%/*}/requirements.txt

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
