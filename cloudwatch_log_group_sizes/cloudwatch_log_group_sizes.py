import boto3
import humanize

groups = {}
pn = boto3.client('logs').get_paginator('describe_log_groups')
for page in pn.paginate():
    for group in page['logGroups']:
        if group['storedBytes'] < 100000000:
            continue
        groups[group['logGroupName']] = group['storedBytes']
for group in sorted(groups.items(), key=lambda x: x[1], reverse=True):
    print(f'{group[0]} {humanize.filesize.naturalsize(group[1])}')
