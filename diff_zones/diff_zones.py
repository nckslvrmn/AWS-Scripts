#!/usr/bin/env python

import sys

import boto3


def get_zones_by_name(client, name):
    zone_ids = {}
    marker = ''
    while True:
        if marker == '':
            resp = client.list_hosted_zones()
        else:
            resp = client.list_hosted_zones(Marker=marker)
        for zone in resp['HostedZones']:
            if zone['Name'] == f"{name}.":
                zone_ids[zone['Id'].split('/')[-1]] = 'private' if zone['Config']['PrivateZone'] else 'public'
        if resp['IsTruncated']:
            marker = resp['NextMarker']
        else:
            break
    return zone_ids


def get_records(client, zone):
    records = []
    next_record_name = ''
    next_record_type = ''
    while True:
        if next_record_name == '':
            resp = client.list_resource_record_sets(HostedZoneId=zone)
        else:
            resp = client.list_resource_record_sets(HostedZoneId=zone, StartRecordName=next_record_name, StartRecordType=next_record_type)
        for record in resp['ResourceRecordSets']:
            if record.get('AliasTarget'):
                records.append({'name': record['Name'], 'type': 'ALIAS', 'alias': [record['AliasTarget']['DNSName']]})
            else:
                records.append(
                    {'name': record['Name'], 'type': record['Type'], 'ttl': record['TTL'], 'targets': sorted([r['Value'] for r in record['ResourceRecords']])}
                )
        if resp['IsTruncated']:
            next_record_name = resp['NextRecordName']
            next_record_type = resp['NextRecordType']
        else:
            break
    return records


def unique_records(list1, list2):
    unique = []
    for i in list1:
        name = i['name']
        rtype = i['type']
        entry2 = list(filter(lambda r: r['name'] == name and r['type'] == rtype, list2))
        if len(entry2) == 0:
            unique.append(i)
    for record in unique:
        if record.get('alias'):
            print(f"  {record['name']} {record['type']} {record['alias']}")
        else:
            print(f"  {record['name']} {record['type']} {record['targets']}")
    return unique


def diff_values(zone_ids, zone_name, zones):
    zone_keys = list(zone_ids.keys())
    list1 = zones[zone_keys[0]]['records']
    list2 = zones[zone_keys[1]]['records']
    for i in list1:
        name = i['name']
        rtype = i['type']
        if name == f"{zone_name}." and rtype in ('NS', 'SOA'):
            continue
        entry2 = list(filter(lambda r: r['name'] == name and r['type'] == rtype, list2))[0]
        if i != entry2:
            print(f'  {name} {rtype}')
            if i.get('alias'):
                print(f"    {zone_ids[zone_keys[0]]} ({zone_keys[0]}) {i['alias']}")
                print(f"    {zone_ids[zone_keys[1]]} ({zone_keys[1]}) {entry2['alias']}\n")
            else:
                print(f"    {zone_ids[zone_keys[0]]} ({zone_keys[0]}) {i['targets']}")
                print(f"    {zone_ids[zone_keys[1]]} ({zone_keys[1]}) {entry2['targets']}\n")


def main():
    client = boto3.client('route53')
    zone_name = sys.argv[1]

    zones = {}
    zone_ids = get_zones_by_name(client, zone_name)
    for zone in zone_ids.keys():
        zones[zone] = {}
    for zone in zones:
        zones[zone]['records'] = get_records(client, zone)

    zone_keys = list(zone_ids.keys())
    print(f'unique records in {zone_name} {zone_ids[zone_keys[0]]} zone')
    unique1 = unique_records(zones[zone_keys[0]]['records'], zones[zone_keys[1]]['records'])
    for record in unique1:
        zones[zone_keys[0]]['records'].remove(record)
    print(f'\nunique records in {zone_name} {zone_ids[zone_keys[1]]} zone')
    unique2 = unique_records(zones[zone_keys[1]]['records'], zones[zone_keys[0]]['records'])
    for record in unique2:
        zones[zone_keys[1]]['records'].remove(record)
    print(f'\nrecords that exist in both zones for {zone_name} but differ in value')
    diff_values(zone_ids, zone_name, zones)


if __name__ == "__main__":
    main()
