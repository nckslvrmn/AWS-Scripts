#!/usr/bin/env python

import sys
import boto3


def main():
    client = boto3.client('logs')
    groups = client.describe_log_groups(logGroupNamePrefix=sys.argv[1])
    paginator = client.get_paginator('describe_log_streams')
    streams = paginator.paginate(
        logGroupName=groups['logGroups'][0]['logGroupName']
    )
    for page in streams:
        for stream in page['logStreams']:
            events = client.get_log_events(
                logGroupName=groups['logGroups'][0]['logGroupName'],
                logStreamName=stream['logStreamName'],
                limit=1
            )
            if len(events.get('events', [])) == 0:
                client.delete_log_stream(
                    logGroupName=groups['logGroups'][0]['logGroupName'],
                    logStreamName=stream['logStreamName']
                )
                print(f"deleted {stream['logStreamName']} log stream")


if __name__ == "__main__":
    main()
