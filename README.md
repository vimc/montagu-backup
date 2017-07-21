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
`/etc/montagu/backup/config.json`. We need multiple configs because we want to
backup different things in different environments. We have two configs 
currently: support and production.

Support runs on the support machine and is responsible for backing up:

* Vault
* Docker registry
* ~~TeamCity~~ (Not implemented yet)

Production runs anywhere we have a Montagu instance deployed and backups 
enabled, but see more about Montagu backup further down.

Here's a sample configuration file:

```
{
    "s3_bucket": "montagu-support",
    "encrypted": false,
    "targets": [
        {
            "type": "directory",
            "path": "/montagu/vault/storage"
        },
        {
            "type": "named_volume",
            "name": "registry_data"
        }
    ]
}
```

Here's what the options mean:

* `s3_bucket`: Amazon S3's file storage is divided into "buckets". Permissions
  and many other options are managed at a bucket level. You can see our buckets
  by logging into the AWS console and choosing the "S3 service". We cannot have
  two separate environments backing up to the same bucket.
* `encrypyted`: If `true` an encryption passphrase is pulled from the vault and
  passed through to Duplicati and used for backup and restore. Note that without
  encryption we still use SSL to send data to and from the cloud, so the data is
  encrypted in transit, althought not at rest. Why turn encryption off? For the
  support backup, the only sensitive part is the vault, which has its own 
  backend encryption. If we further encrypted the vault backup, we'd then need
  to decrypt the vault to get the passphrase to decrypt the vault. We do use
  encryption for the production backup.

## Targets
Targets are what should be backed up (and restored). Each target must specify a
"type", which can be `directory`, `named_volume` and `container`. Each of these
requires further options.

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
   will be prompted for Vault (GitHub) access token.
2. `backup.py`: Runs a one-off backup. Output is also logged to 
   `/var/log/duplicati`.
3. `schedule.py`: Uses cron to schedule `backup.py` to be run at 2am daily.
4. `restore.py`: Restores from remote backup.
5. `cli.py`: Passes arguments through to Duplicati CLI, filling in secrets and
   the remote URL. Usage example: `./cli.py list 0`, to see all files in the
   most recent backup.

# Montagu backup
In addition to backing up infrastructure on the support machine we use this
module to backup and restore a live Montagu instance. However, we don't do this
directly. Instead, the `deploy.py` script in the [main Montagu repo](https://github.com/vimc/montagu)
configures the backup and invokes the above scripts automatically.