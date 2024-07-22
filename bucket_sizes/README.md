# AWS S3 Bucket Sizes

This script will generate CSV file given the sizes of all major storage tiers
for all s3 buckets in an AWS account that you can import into various
spreadsheet tools.

To Run:

```
> AWS_PROFILE=blah ./bucket_sizes.py

usage: bucket_sizes.py [-h] [-b BUCKET] [--humanize] [--json]

options:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
  --humanize
  --json
```

For pretty google sheets number formatting, use this custom number format:

```
[<1000000000]0.00,," MB";[<1000000000000]0.00,,," GB";0.00,,,," TB"
```
