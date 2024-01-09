# List Empty S3 Buckets

Lists all S3 buckets with no current contents. This script is not sensitive to
buckets which contain only non-current version objects.

To run:

```
AWS_PROFILE=blah ./list_empty_buckets.py
```
