#!/usr/bin/env python3

import argparse
import csv
import json
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


def humanize_bytes(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def construct_query(bucket_name):
    queries = []
    for stype in STORAGE_TYPES:
        queries.append(
            {
                "Id": stype.lower(),
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/S3",
                        "MetricName": "BucketSizeBytes",
                        "Dimensions": [
                            {"Name": "BucketName", "Value": bucket_name},
                            {"Name": "StorageType", "Value": stype},
                        ],
                    },
                    "Period": 86400,
                    "Stat": "Maximum",
                },
            }
        )
    return queries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bucket", default=None)
    parser.add_argument("--humanize", action="store_true", default=False)
    parser.add_argument("--json", action="store_true", default=False)
    args = parser.parse_args()

    sess = boto3.session.Session()
    s3 = sess.client("s3")
    cw = sess.client("cloudwatch")
    sizes = []
    buckets = (
        [args.bucket]
        if args.bucket is not None
        else [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
    )

    for bucket in buckets:
        if (
            s3.head_bucket(Bucket=bucket)["ResponseMetadata"]["HTTPHeaders"][
                "x-amz-bucket-region"
            ]
            != sess.region_name
        ):
            continue
        bucket_sizes = {"Name": bucket}
        resp = cw.get_metric_data(
            MetricDataQueries=construct_query(bucket),
            StartTime=(datetime.today() - timedelta(days=3)),
            EndTime=(datetime.today() - timedelta(days=2)),
        )
        for metric in resp["MetricDataResults"]:
            if len(metric["Values"]) > 0:
                bucket_sizes[metric["Label"]] = (
                    humanize_bytes(metric["Values"][0])
                    if args.humanize
                    else metric["Values"][0]
                )
        sizes.append(bucket_sizes)

    if args.json:
        print(json.dumps(sizes, indent=2))
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=["Name"] + STORAGE_TYPES)
        w.writeheader()
        w.writerows(sizes)


if __name__ == "__main__":
    main()
