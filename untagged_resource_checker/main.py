import boto3
from requests import post 
from os import environ

slack_webhook = environ["SLACK_WEBHOOK"]

# accept input / pull list of accepted tags from elsewhere
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

    #TODO: add region name to returned data to enable termination + easier finding and tagging of resource
    return untagged_instances

def notify_slack(instance_ids):
    instance_ids = '\n'.join(instance_ids)
    payload = f"{{'text' : 'The following instance_ids are untagged: ```{instance_ids}```'}}"
    r = post(slack_webhook, data=payload, headers={'Content-Type': 'application/json'})

    if r.status_code != 200:
        print(f'Slack webhook request error code {r.status_code}, the response is {r.text}')


def main():
    regions = get_regions()
    untagged_instances = []

    for r in regions:
        print(f'Checking {r} for untagged instances..')
        untagged_instances += get_untagged_instances_by_region(r)

    # ask what to do with these instances (notify, terminate, etc)
    print(untagged_instances)
    notify_slack(untagged_instances)
    print("Done")

if __name__ == "__main__":
    main()

