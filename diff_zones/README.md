# Diff Route53 DNS Zones

Compares the records in equally named zones in DNS where one zone is public and
one zone is private. This is useful when doing split-brain DNS and you want to
ensure that only records exist in private vs public or vice versa.

To run:

```
AWS_PROFILE=blah ./diff_zones.py mycooldomain.com
```
