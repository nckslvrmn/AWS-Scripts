#!/usr/bin/env python3

import argparse
import time

import boto3
from botocore.exceptions import ClientError


class GlacierRestorer:
    def __init__(self, args):
        self.s3_client = boto3.client("s3")
        self.args = args
        self.keys = []

    def log(self, level, message):
        if (level == "ERROR") or self.args.verbose:
            print(f"{level}: {message}")

    def collect_keys(self):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.args.bucket, Prefix=self.args.path)
        for page in pages:
            try:
                for obj in page["Contents"]:
                    self.keys.append(obj["Key"])
            except KeyError:
                continue

    def restore_object(self, key):
        try:
            response = self.s3_client.restore_object(
                Bucket=self.args.bucket,
                Key=key,
                RestoreRequest={
                    "Days": self.args.days,
                    "GlacierJobParameters": {"Tier": self.args.tier},
                },
            )
            status = response["ResponseMetadata"]["HTTPStatusCode"]
            if status > 400:
                self.log(
                    "ERROR",
                    f"object restore failed for {key} with response {response}",
                )
            else:
                self.log("VERBOSE", f"triggered object restore for {key}")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "RestoreAlreadyInProgress":
                self.log("VERBOSE", f"object restore already in progress for {key}")
            else:
                self.log(
                    "ERROR",
                    f"object restore failed for {key}: {e}",
                )

    def is_object_restored(self, key):
        response = self.s3_client.head_object(Bucket=self.args.bucket, Key=key)
        status = response["ResponseMetadata"]["HTTPHeaders"].get("x-amz-restore")
        if status != 'ongoing-request="true"':
            self.log("VERBOSE", f"restore complete for {key}")
            self.keys.remove(key)


def restore():
    parser = argparse.ArgumentParser(
        prog="glacier_restorer.py",
        description="a script to restore all objects in a given bucket and path",
    )
    parser.add_argument("-b", "--bucket", required=True)
    parser.add_argument("-p", "--path", required=True)
    parser.add_argument("-d", "--days", default=7)
    parser.add_argument(
        "-t", "--tier", default="Standard", choices=["Standard", "Bulk", "Expedited"]
    )
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = parser.parse_args()

    gr = GlacierRestorer(args)
    gr.collect_keys()

    to_restore_count = len(gr.keys)
    print(f"INFO: found {to_restore_count} keys to restore from glacier")

    for key in gr.keys:
        gr.restore_object(key)

    while len(gr.keys) > 0:
        for key in gr.keys:
            gr.is_object_restored(key)
        print(f"INFO: {to_restore_count - len(gr.keys)} completed, {len(gr.keys)} left")
        time.sleep(60)


if __name__ == "__main__":
    restore()
