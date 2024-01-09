#!/usr/bin/env python3

import boto3

account_id = boto3.client('sts').get_caller_identity().get('Account')
ec2 = boto3.client('ec2')

snaps = []
snap_pag = ec2.get_paginator('describe_snapshots')
for page in snap_pag.paginate(OwnerIds=[account_id]):
    for snapshot in page['Snapshots']:
        snaps.append(snapshot['SnapshotId'])


vol_snaps = []
vols_pag = ec2.get_paginator('describe_volumes')
for page in vols_pag.paginate():
    for vol in page['Volumes']:
        vol_snaps.append(vol['SnapshotId'])


ami_snaps = []
for ami in ec2.describe_images(Owners=[account_id])['Images']:
    for dev in ami['BlockDeviceMappings']:
        if dev.get('Ebs', {}).get('SnapshotId') is None:
            continue
        ami_snaps.append(dev['Ebs']['SnapshotId'])


orphaned = []
for snap in snaps:
    if (snap in vol_snaps) or (snap in ami_snaps):
        continue
    orphaned.append(snap)

orphan_info = ec2.describe_snapshots(SnapshotIds=orphaned)

print(orphan_info)
