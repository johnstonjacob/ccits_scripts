
import boto3
tag_keys = ['ce_name', 'test_tag']
tag_value = ['jacob_cse']

print(tag_keys, tag_value)
resource_type_filters = ['ec2:instance']
def get_resources_by_tag_in_region(region):
    tagging_client = boto3.client('resourcegroupstaggingapi', region_name=region)

    resources = tagging_client.get_resources(TagFilters=[{
            'Key': tag_key,
#            'Values': tag_value
        }],
        ResourceTypeFilters= resource_type_filters
        )

    return resources['ResourceTagMappingList']

def main():
    regions = get_regions()
    resources = []

    for r in regions:
        print(f'Checking {r} for untagged instances..')
        resources.append(get_resources_by_tag_in_region(r))

    print(resources)
