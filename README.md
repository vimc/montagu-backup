# Backup
This repository is a set of Python scripts that wrap around 
[Duplicati CLI](https://www.duplicati.com/). Duplicati allows backup to multiple
different backends, with progressive backups (i.e. only sending a diff) and 
optional encryption.

We are using Amazon S3 as a backend. If you already have access to the Amazon
Web Console, you can log at [montagu.signin.aws.amazon.com/console](https://montagu.signin.aws.amazon.com/console).
You can then grant new users access by going to the IAM service. From there add
a new user and give them access to the "Developers" group.

# Configuration
We have a simple JSON file that configures our backup tool. It lives at
`config.json`. We need multiple configs because we want to
backup different things in different environments. We have one config
currently: annex.json. It backs up everything from the starport (see
[BB8](https://github.com/vimc/bb8) for more on this) to individual
buckets on S3.

## Sample configuration file
Here's a sample configuration file:

```
{
    "targets": [
        {
            "id": "vault",
            "type": "directory",
            "path": "/montagu/vault/storage",
            "s3_bucket": "montagu-vault",
            "encrypted": false
        },
        {
            "id": "registry",
            "type": "named_volume",
            "name": "registry_data",
            "s3_bucket": "montagu-registry",
            "encrypted": true
        }
    ]
}
```

Here's what the options mean:

## Targets
Targets are what should be backed up (and restored). Each target must specify a
"type", which can be `directory`, `named_volume` and `container`. Each of these
requires further options.

### Common options for all targets
* `id`: A unique id for the target.
* `s3_bucket`: Amazon S3's file storage is divided into "buckets". Permissions
  and many other options are managed at a bucket level. You can see our buckets
  by logging into the AWS console and choosing the "S3 service". We cannot have
  two separate environments backing up to the same bucket.
* `encrypted`: If `true` an encryption passphrase is pulled from the vault and
  passed through to Duplicati and used for backup and restore. Note that without
  encryption we still use SSL to send data to and from the cloud, so the data is
  encrypted in transit, although not at rest. Why turn encryption off? For the
  support backup, the only sensitive part is the vault, which has its own
  backend encryption. If we further encrypted the vault backup, we'd then need
  to decrypt the vault to get the passphrase to decrypt the vault. We do use
  encryption for the production backup.

### Directory
Simplest option. Requires a `path` to a directory. On a restore it will first
create the directory if it doesn't exist.

### Named volume
Requires the `name` of the volume. On a restore it will first create the named
volume using Docker CLI, if it doesn't exist. It determines the mountpoint of 
the volume automatically and passes it through to the Duplicati CLI.

### Container
Requires these fields:

* `name`: The name of the container to backup
* `path`: A file to use as a staging area. Data is dumped from the container to
  this path on backup, and then path is passed to Duplicati. Similarly on 
  restore, Duplicati restores to this path and then we import it into the 
  container.
* `backup_script`: A script to run in the container using `docker exec` to dump
  data out to the specified path. The script must be an array in the format 
  expected by Python's [subprocess module](https://docs.python.org/3/library/subprocess.html).
  The output will be redirected to `path`.
* `restore_script`: A script to run in the container using `docker exec`. First,
  the restored file is copied from `path` in the host machine to `/tmp/backup`
  inside the container. Your script should expect to read from there. Again,
  the script must be an array for Python's [subprocess module](https://docs.python.org/3/library/subprocess.html).

# Scripts
There are five entrypoints to the backup module. All need be run as root.

1. `setup.sh`: This installs Duplicati and fetches secrets from the Vault. You
   will be prompted for Vault (GitHub) access token. Do not run as root -
   it will use sudo to request elevation if needed.
2. `backup.py`: Runs a one-off backup. Output is also logged to 
   `/var/log/duplicati`.
3. `schedule.py`: Uses cron to schedule `backup.py` to be run at 2am daily.
4. `restore.py`: Restores from remote backup.
5. `cli.py`: Passes arguments through to Duplicati CLI, filling in secrets and
   the remote URL. Usage example: `./cli.py TARGET list 0`, to see all files in the
   most recent backup (for target with id TARGET)
