#!/usr/bin/env python3

import json
import boto3
import sys

pricing_client = boto3.client('pricing', region_name='us-east-1')


def get_ec2_price(instance_type):
    response = pricing_client.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
            {'Type': 'TERM_MATCH', 'Field': 'licenseModel', 'Value': 'No License required'},
        ],
    )

    data = {'costs': {}}
    for priceItem in response['PriceList']:
        parsed = json.loads(priceItem)
        data['vcpu'] = parsed['product']['attributes']['vcpu']
        data['memory'] = parsed['product']['attributes']['memory']
        od_price = list(parsed['terms']['OnDemand'].values())[0]
        dimensions = list(od_price['priceDimensions'].values())[0]
        data['costs'][parsed['product']['attributes']['operatingSystem']] = float(dimensions['pricePerUnit']['USD'])
    return data


if __name__ == '__main__':
    itype = sys.argv[1]
    price_data = get_ec2_price(itype)
    print(f"{itype}: {price_data['vcpu']} core {price_data['memory']} memory\n")
    for os in ['Linux', 'Windows']:
        hourly = '${:,.4f}'.format(price_data['costs'][os])
        daily = '${:,.4f}'.format(price_data['costs'][os] * 24)
        weekly = '${:,.4f}'.format(price_data['costs'][os] * 168)
        monthly = '${:,.4f}'.format(price_data['costs'][os] * 730)
        print(f'{os} costs:\n  {hourly}/hour\n  {daily}/daily\n  {weekly}/weekly\n  {monthly}/monthly\n')
