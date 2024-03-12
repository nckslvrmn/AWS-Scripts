#!/usr/bin/env python3

import sys

import boto3


def delete_resources(client, image):
    client.deregister_image(ImageId=image['id'])
    print(f"{image['id']} deleted")

    for snap in image["snaps"]:
        client.delete_snapshot(SnapshotId=snap)
        print(f'{snap} deleted')


def main():
    prefix = sys.argv[1]

    account_id = boto3.client('sts').get_caller_identity().get('Account')
    ec2 = boto3.client('ec2')
    amis = ec2.describe_images(Owners=[str(account_id)])

    to_delete = []
    for image in amis['Images']:
        if image['Name'].startswith(prefix):
            snaps = [
                snap.get('Ebs', {}).get('SnapshotId') for snap in image.get('BlockDeviceMappings', {}) if snap.get('Ebs', {}).get('SnapshotId') is not None
            ]
            to_delete.append({'id': image['ImageId'], 'snaps': [snap for snap in snaps if snap is not None]})

    for ami in to_delete:
        delete_resources(ec2, ami)


if __name__ == "__main__":
    main()
