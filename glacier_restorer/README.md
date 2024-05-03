# Glacier Restorer

Glacier restores all objects in a given bucket and path. Has arguments for
customizing restore call.

To run:

```
AWS_PROFILE=blah ./glacier_restorer.py ARGS
```

Args:

```
usage: glacier_restorer.py [-h] -b BUCKET -p PATH [-d DAYS] [-t {Standard,Bulk,Expedited}] [-v]

a script to restore all objects in a given bucket and path

options:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
  -p PATH, --path PATH
  -d DAYS, --days DAYS
  -t {Standard,Bulk,Expedited}, --tier {Standard,Bulk,Expedited}
  -v, --verbose
```
