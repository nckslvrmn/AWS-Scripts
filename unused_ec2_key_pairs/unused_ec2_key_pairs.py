#!/usr/bin/env python3

import boto3

ec2 = boto3.client("ec2")

keys = [key["KeyName"] for key in ec2.describe_key_pairs()["KeyPairs"]]

paginator = ec2.get_paginator("describe_instances")
for page in paginator.paginate():
    for res in page["Reservations"]:
        for instance in res["Instances"]:
            if instance.get("KeyName") in keys:
                keys.remove(instance["KeyName"])

for key in sorted(keys):
    print(key)
