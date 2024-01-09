# delete empty cloudwatch log streams

This script deletes any empty cloudwatch stream that has been emptied due to log
retention policies.

To run:

```
AWS_PROFILE=blah ./delete_empty_cloudwatch_logstreams.py NAME_OF_CW_LOG_GROUP
```
