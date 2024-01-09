import sys

import boto3


def delete_resources(client, image):
    client.deregister_image(ImageId=image['id'])
    print(f"{image['id']} deleted")

    for snap in image["snapshots"]:
        client.delete_snapshot(SnapshotId=snap)
        print(f'{snap} deleted')


def handler(*_):
    pattern = sys.argv[1]

    account_id = boto3.client('sts').get_caller_identity().get('Account')
    ec2 = boto3.client('ec2')
    amis = ec2.describe_images(Owners=[str(account_id)], Filters=[{'Name': 'name', 'Values': [pattern]}])

    to_delete = {}
    for image in amis['Images']:
        first_name_section = image['Name'].split('20')[0]
        if to_delete.get(first_name_section) is None:
            to_delete[first_name_section] = {}
        snaps = [snap.get('Ebs', {}).get('SnapshotId') for snap in image.get('BlockDeviceMappings', {}) if snap.get('Ebs', {}).get('SnapshotId') is not None]
        if to_delete[first_name_section].get(image['Name']) is None:
            to_delete[first_name_section][image['Name']] = {}
        to_delete[first_name_section][image['Name']]['id'] = image['ImageId']
        to_delete[first_name_section][image['Name']]['snapshots'] = snaps

    for name_pattern in to_delete.items():
        sort = dict(sorted(name_pattern[1].items(), reverse=True))
        del sort[list(sort.keys())[0]]
        for image in sort.items():
            delete_resources(ec2, image[1])


if __name__ == "__main__":
    handler()
