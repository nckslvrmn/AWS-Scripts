#!/usr/bin/env python3

import sys

import boto3

from prettytable import PrettyTable


def get_attribute(attributes, key):
    for attribute in attributes:
        if attribute['name'] == key:
            if attribute.get('value') is not None:
                return attribute['value']
            else:
                return attribute['name']


def ecs_instance_info(ecs, cluster):
    instances = []
    resp = ecs.list_container_instances(cluster=cluster)
    if len(resp['containerInstanceArns']) == 0:
        return []
    instance_info = ecs.describe_container_instances(
        cluster=cluster,
        containerInstances=resp['containerInstanceArns'],
    )
    for instance in instance_info['containerInstances']:
        instances.append(
            {
                'id': instance['ec2InstanceId'],
                'capacity_provider': instance['capacityProviderName'],
                'instance_type': get_attribute(instance['attributes'], 'ecs.instance-type'),
                'ami_id': get_attribute(instance['attributes'], 'ecs.ami-id'),
                'running_tasks': instance['runningTasksCount'],
                'agent_version': instance.get('versionInfo', {}).get('agentVersion'),
                'docker_version': instance.get('versionInfo', {}).get('dockerVersion'),
                'has_exec': True if get_attribute(instance['attributes'], 'ecs.capability.execute-command') is not None else False,
            }
        )
    return sorted(instances, key=lambda k: k['capacity_provider'])


def table_print(instance_info):
    table = PrettyTable()
    table.field_names = instance_info[0].keys()
    for instance in instance_info:
        table.add_row(instance.values())
    print(table)


def main():
    ecs = boto3.client('ecs')
    clusters = ecs.list_clusters(maxResults=100)['clusterArns']

    for cluster in clusters:
        instance_info = ecs_instance_info(ecs, cluster)
        if len(instance_info) == 0:
            continue
        print(f"{cluster.upper()} - {len(instance_info)} hosts")
        table_print(instance_info)
        print()


if __name__ == "__main__":
    main()
