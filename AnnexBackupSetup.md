This probably doesn't really need documenting, as its a straightforward 
application of our general backup mechanism, but I thought I'd be careful:

1. `ssh annex.montagu.dide.ic.ac.uk`
1. `sudo su`
1. `cd /home/montagu`
1. Clone the backup repo if it isn't already there 
   (`git clone git@github.com:vimc/montagu-backup`)
1. `cd montagu-backup`
1. `./setup.sh`. This will (eventually) complain about the lack of a config 
   file. Adapt the example it gives you to copy the annex config into the right
   place. Then run `./setup.sh` again.
1. Now you can run `./restore.py`, or `./schedule.py` as appropriate. (Or 
   `backup.py` if you are starting again with a brand new annex for some 
   reason.)
