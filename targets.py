import logging
from os import makedirs
from os.path import isdir, dirname
from subprocess import run, PIPE


class Target:
    def __init__(self, id, bucket, encrypted, max_versions):
        self.id = id
        self.bucket = bucket
        self.encrypted = encrypted
        self.max_versions = max_versions

    @property
    def remote_url(self):
        return "s3://{bucket}".format(bucket=self.bucket)


class DirectoryTarget(Target):
    def __init__(self, path, id, bucket, encrypted, max_versions):
        super().__init__(id, bucket, encrypted, max_versions)
        self.path = path

    @property
    def paths(self):
        return [self.path]

    def before_restore(self):
        if not isdir(self.path):
            print("Creating empty directory " + self.path)
            makedirs(self.path)

    def after_restore(self):
        pass

    def before_backup(self):
        pass


class NamedVolumeTarget(Target):
    def __init__(self, name, id, bucket, encrypted, max_versions):
        super().__init__(id, bucket, encrypted, max_versions)
        self.name = name

    @property
    def paths(self):
        return [self._get_mountpoint()]

    def _get_mountpoint(self):
        return run(
            ["docker", "volume", "inspect", self.name, "-f", "{{ .Mountpoint }}"],
            stdout=PIPE, universal_newlines=True
        ).stdout.strip()

    def _volume_exists(self):
        text = run(
            ["docker", "volume", "ls", "-q"],
            stdout=PIPE, universal_newlines=True
        ).stdout
        names = text.split('\n')
        return self.name in names

    def before_restore(self):
        if not self._volume_exists():
            print("Creating docker volume with name '{}'".format(self.name))
            run(["docker", "volume", "create", "--name", self.name], stdout=PIPE)

    def after_restore(self):
        pass

    def before_backup(self):
        pass


class ContainerTarget(Target):
    def __init__(self, name, path, backup_script, restore_script, id, bucket,
                 encrypted, max_versions):
        super().__init__(id, bucket, encrypted, max_versions)
        self.name = name
        self.path = path
        self.backup_script = backup_script
        self.restore_script = restore_script

    @property
    def paths(self):
        return [self.path]

    def _make_empty_dir(self):
        directory = dirname(self.path)
        if not isdir(directory):
            print("Creating empty directory " + directory)
            logging.info("Creating empty directory " + directory)
            makedirs(directory)

    def before_restore(self):
        self._make_empty_dir()

    def after_restore(self):
        print("Importing {path} into {name}".format(name=self.name, path=self.path))
        full_target = "{container}:{path}".format(container=self.name, path="/tmp/backup")
        run(["docker", "cp", self.path, full_target], check=True)
        run(["docker", "exec", self.name] + self.restore_script, check=True)

    def before_backup(self):
        self._make_empty_dir()
        logging.info("Dumping data from {name} to {path}".format(name=self.name, path=self.path))
        with open(self.path, 'w') as f:
            run(["docker", "exec", self.name] + self.backup_script, stdout=f, check=True)
