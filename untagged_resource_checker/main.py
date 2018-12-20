from requests import post 
from os import environ

import boto3

# TODO: accept input / pull list of accepted tags from elsewhere
tag_keys = ['ce_name', 'test_tag']

slack_webhook = environ["SLACK_WEBHOOK"]

print(tag_keys)

def get_regions():
    ec2_client = boto3.client('ec2')

    return [r['RegionName'] for r in ec2_client.describe_regions()['Regions']]


def get_untagged_instances_by_region(region):
    instances = [i for i in boto3.resource('ec2', region_name=region).instances.all()]

    untagged_instances = []

    for i in instances:
        if not any(key in tag_keys for key in [t['Key'] for t in i.tags]):
            if i['state']['Code'] == 16:
                print(i.instance_id)
                untagged_instances.append({'instance_id': i.instance_id, 'region_name': region})

    return untagged_instances

def notify_slack(instance_ids):
    instance_ids = '\n'.join(i["instance_id"] + " in " + i["region_name"]  for i in instance_ids)
    payload = f"{{'text' : 'The following instance_ids are untagged: ```{instance_ids}```'}}"
    r = post(slack_webhook, data=payload, headers={'Content-Type': 'application/json'})

    if r.status_code != 200:
        print(f'Slack webhook request error code {r.status_code}, the response is {r.text}')

def group_instances_by_region(instances):
    instances_by_region = {}
    for instance in instances:
        instance_id = instance['instance_id']
        region = instance['region_name']
        if region not in instances_by_region:
            instances_by_region[region] = [instance_id]
        else:
            instances_by_region[region].append(instance_id) 

    return instances_by_region

def shut_down_instances_by_region(instances_by_region):
    for region, instances in instances_by_region.items():
        ec2_client = boto3.client('ec2', region_name=region)
        print(f'Shutting down untagged instances in {region}')

        res = ec2_client.stop_instances(InstanceIds=instances, DryRun=True)
        print('Result for {region}: {res}')

def main():
    regions = get_regions()
    untagged_instances = []

    for r in regions:
        print(f'Checking {r} for untagged instances..')
        untagged_instances += get_untagged_instances_by_region(r)

    notify_slack(untagged_instances)
    shut_down_instances_by_region(group_instances_by_region(untagged_instances))
    print("Done")

if __name__ == "__main__":
    main()

