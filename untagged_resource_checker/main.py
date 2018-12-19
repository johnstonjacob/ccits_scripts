import boto3

tag_keys = ['ce_name', 'test_tag']

print(tag_keys)

def get_regions():
    ec2_client = boto3.client('ec2')

    return [r['RegionName'] for r in ec2_client.describe_regions()['Regions']]


def get_untagged_instances_by_region(region):
    instances = [i for i in boto3.resource('ec2', region_name=region).instances.all()]

    untagged_instances = []

    for i in instances:
        if not any(key in tag_keys for key in [t['Key'] for t in i.tags]):
            print(i.instance_id)
            untagged_instances.append(i.instance_id)

    return untagged_instances

def main():
    regions = get_regions()
    untagged_instances = []

    for r in regions:
        print(f'Checking {r} for untagged instances..')
        untagged_instances += get_untagged_instances_by_region(r)

    print(untagged_instances)
    print("Done")

if __name__ == "__main__":
    main()

