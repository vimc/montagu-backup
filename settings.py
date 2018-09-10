import json
import os
from os.path import join, isfile
from subprocess import check_output

from targets import DirectoryTarget, NamedVolumeTarget, ContainerTarget

root_path = os.path.dirname(os.path.realpath(__file__))
config_path = join(root_path, "config.json")
secrets_path = join(root_path, "secrets.json")

log_dir = '/var/log/duplicati'


class Settings:
    def __init__(self):
        with open(config_path, 'r') as f:
            config = json.load(f)
        if isfile(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
        else:
            secrets = {}

        self.secrets = secrets
        self.targets = list(Settings.parse_target(t) for t in config["targets"])
        ids = [t.id for t in self.targets]
        if list(set(ids)) != ids:
            raise Exception("Targets with duplicate IDs were found in config")


    @classmethod
    def parse_target(cls, data):
        t = data["type"]
        id = data["id"]
        bucket = data["s3_bucket"]
        encrypted = data["encrypted"]

        if t == "directory":
            return DirectoryTarget(data["path"], id, bucket, encrypted)
        elif t == "named_volume":
            return NamedVolumeTarget(data["name"], id, bucket, encrypted)
        elif t == "container":
            return ContainerTarget(data["name"],
                                   data["path"],
                                   data["backup_script"],
                                   data["restore_script"],
                                   id, bucket, encrypted)
        else:
            raise Exception("Unsupported target type: " + t)


def shared_args(settings, encrypted):
    secrets = settings.secrets
    args = [
        # See https://github.com/duplicati/duplicati/issues/2231#issuecomment-419942565
        # for why we have this first option
        "--s3-server-name=s3.eu-west-2.amazonaws.com",
        "--aws_access_key_id={aws_access_key_id}".format(**secrets),
        "--aws_secret_access_key={aws_secret_access_key}".format(**secrets),
        "--use-ssl"
    ]
    if encrypted:
        args += ["--passphrase={passphrase}".format(**secrets)]
    else:
        args += ["--no-encryption=true"]
    return args


def load_settings():
    return Settings()


def get_secret(name):
    path = "secret/backup/{}".format(name)
    return check_output(["vault", "read", "-field=value", path]).decode('utf-8')


def save_secrets(get_passphrase):
    if not isfile(secrets_path):
        secrets = {
            "aws_access_key_id": get_secret("aws_access_key_id"),
            "aws_secret_access_key": get_secret("aws_secret_access_key"),
        }
        if get_passphrase:
            secrets["passphrase"] = get_secret("passphrase")

        with open(secrets_path, 'a'):  # Create file if does not exist
            pass
        os.chmod(secrets_path, 0o600)
        with open(secrets_path, 'w') as f:
            json.dump(secrets, f)
