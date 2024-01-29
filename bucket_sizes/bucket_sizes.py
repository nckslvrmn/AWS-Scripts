#!/usr/bin/env python3

import csv
import sys

from datetime import datetime
from datetime import timedelta

import boto3

STORAGE_TYPES = [
    "StandardStorage",
    "IntelligentTieringFAStorage",
    "IntelligentTieringIAStorage",
    "IntelligentTieringAAStorage",
    "IntelligentTieringAIAStorage",
    "IntelligentTieringDAAStorage",
    "StandardIAStorage",
    "OneZoneIAStorage",
    "ReducedRedundancyStorage",
    "GlacierInstantRetrievalStorage",
    "GlacierStorage",
    "GlacierStagingStorage",
    "DeepArchiveStorage",
    "DeepArchiveStagingStorage",
]


def construct_query(bucket_name):
    queries = []
    for stype in STORAGE_TYPES:
        queries.append(
            {
                'Id': stype.lower(),
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/S3',
                        'MetricName': 'BucketSizeBytes',
                        'Dimensions': [
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': stype},
                        ],
                    },
                    'Period': 86400,
                    'Stat': 'Maximum',
                },
            }
        )
    return queries


def main():
    sess = boto3.session.Session()
    s3 = sess.client('s3')
    cw = sess.client('cloudwatch')
    sizes = []
    if len(sys.argv) > 1:
        buckets = [sys.argv[1]]
    else:
        buckets = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]
    for bucket in buckets:
        if s3.head_bucket(Bucket=bucket)['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region'] != sess.region_name:
            continue
        bucket_sizes = {'Name': bucket}
        resp = cw.get_metric_data(
            MetricDataQueries=construct_query(bucket), StartTime=(datetime.today() - timedelta(days=3)), EndTime=(datetime.today() - timedelta(days=2))
        )
        for metric in resp['MetricDataResults']:
            if len(metric['Values']) > 0:
                value = metric['Values'][0]
            else:
                value = 0
            bucket_sizes[metric['Label']] = value
        sizes.append(bucket_sizes)
    w = csv.DictWriter(sys.stdout, fieldnames=['Name'] + STORAGE_TYPES)
    w.writeheader()
    w.writerows(sizes)


if __name__ == "__main__":
    main()
