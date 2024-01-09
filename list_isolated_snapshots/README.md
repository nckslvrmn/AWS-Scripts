# List Isolated Snapshots

In an account where all snapshots are expected to be associated with volumes or
AMIs, this script can identify and list any snapshot not associated with either.

To run:

```
AWS_PROFILE=blah ./list_isolated_snapshots.py
```
