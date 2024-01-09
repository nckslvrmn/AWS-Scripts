#!/usr/bin/env python3

import boto3

s3 = boto3.client('s3')
for b in [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]:
    objects = s3.list_objects_v2(Bucket=b, MaxKeys=1)
    if len(objects.get('Contents', [])) == 0:
        print(b)
