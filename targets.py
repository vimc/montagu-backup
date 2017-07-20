from os import makedirs
from os.path import isdir, dirname
from subprocess import run, PIPE, check_output

import logging


class DirectoryTarget:
    def __init__(self, path):
        self.path = path

    @property
    def paths(self):
        return [self.path]

    @property
    def id(self):
        return "Directory: " + self.path

    def before_restore(self):
        if not isdir(self.path):
            print("Creating empty directory " + self.path)
            makedirs(self.path)

    def after_restore(self):
        pass

    def before_backup(self):
        pass


class NamedVolumeTarget:
    def __init__(self, name):
        self.name = name

    @property
    def paths(self):
        return [self._get_mountpoint()]

    @property
    def id(self):
        return "Named volume: " + self.name

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


class ContainerTarget:
    def __init__(self, name, path, backup_script, restore_script):
        self.name = name
        self.path = path
        self.backup_script = backup_script
        self.restore_script = restore_script

    @property
    def paths(self):
        return [self.path]

    @property
    def id(self):
        return "Container: " + self.name

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
