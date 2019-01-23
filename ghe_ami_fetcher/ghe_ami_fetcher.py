from sys import argv

from distutils.version import StrictVersion
from re import search

import boto3

def get_regions():
    ec2_client = boto3.client('ec2')

    return [r['RegionName'] for r in ec2_client.describe_regions()['Regions']]

def get_ghe_ami_by_region(region):
    ec2_client = boto3.client('ec2', region_name=region)
    version_re = r'([\d.]+)'
    ghe_amis_by_version = []

    res = ec2_client.describe_images(
            Owners=["895557238572"],
          )

    for ami in res['Images']:
        image_version, image_id = ami['Name'], ami['ImageId']
        image_version = search(version_re, image_version).group(1)
        ghe_amis_by_version.append((image_version, image_id, region))  

    return ghe_amis_by_version

def get_latest_version(amis):
    latest = amis[0][0]

    for ami in amis:
        version = ami[0]
        if StrictVersion(version) > StrictVersion(latest):
            latest = version

    print(latest, "is the latest version. Using that.")
    return latest

def get_ami_by_version(amis, version):
    amis_by_version = []

    for region in list(amis.values()):
        for ami in region:
            if ami[0] == version:
                amis_by_version.append(ami)
                break
    return amis_by_version

def tf_var_formatter(amis):
    for ami in amis:
        print(ami[2], "=", ami[1])

def main():
    ghe_amis = {}


    regions = get_regions()

    for r in regions:
        ghe_amis[r] = get_ghe_ami_by_region(r)

    if len(argv) > 1:
        ghe_version = argv[1] 
    else:
        sample_region = list(ghe_amis.values())[0]
        ghe_version = get_latest_version(sample_region)

    ghe_amis_region_by_version = get_ami_by_version(ghe_amis, ghe_version)
    tf_var_formatter(ghe_amis_region_by_version)
     
if __name__ == "__main__":
    main()

