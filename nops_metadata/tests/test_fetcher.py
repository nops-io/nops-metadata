import boto3
import pytest

from nops_metadata import METAMAP
from nops_metadata import MetaFetcher


def test_meta_fetcher_init(metafetcher: MetaFetcher):
    assert metafetcher


def test_metamap_naming():
    """Metamap naming must be strongly consistent"""
    for key, element in METAMAP.items():
        assert element is not None
        _, entity_name = key.split("_", 1)

        fetch_method = element["fetch_method"]
        assert isinstance(fetch_method, str)
        _, entity_from_fetch_method = fetch_method.split("_", 1)
        assert entity_name == entity_from_fetch_method


def test_meta_fetcher_region_list(metafetcher: MetaFetcher):
    assert metafetcher.metadata_regions(metadata_type="ec2_instances")


def test_meta_fetcher_region_list_wrong_name(metafetcher: MetaFetcher):
    assert not metafetcher.metadata_regions(metadata_type="unknown_servicecall")


@pytest.fixture
def ecs_clusters(metafetcher: MetaFetcher):
    resources = metafetcher.fetch(metadata_type="ecs_clusters", region_name="us-west-2")
    return [r for r in resources]


@pytest.fixture
def ec2_instances(metafetcher: MetaFetcher):
    resources = metafetcher.fetch(metadata_type="ec2_instances", region_name="us-west-2")
    return [r for r in resources]


@pytest.fixture
def elbv2_target_groups(metafetcher: MetaFetcher):
    resources = metafetcher.fetch(metadata_type="elbv2_target_groups", region_name="us-west-2")
    return [r for r in resources]


def test_meta_fetcher_pulling_listing(ecs_clusters):
    assert ecs_clusters
    assert isinstance(ecs_clusters, list)

    for element in ecs_clusters:
        assert isinstance(element, dict)

    assert all(ecs_clusters)


def test_meta_fetcher_metadata_types(metafetcher):
    """Confirm that all calls are working"""
    for metadata_type in metafetcher.metadata_types:
        assert all(metafetcher.fetch(metadata_type=metadata_type, region_name="eu-central-1"))


def test_meta_fetcher_schema_export(metafetcher: MetaFetcher):
    for metadata_type in metafetcher.metadata_types:
        spark_schema = metafetcher.schema(metadata_type=metadata_type)
        postgres_schema = metafetcher.postgres_schema(metadata_type=metadata_type)
        assert spark_schema
        assert postgres_schema


def test_meta_fetcher_pulling_resource_details_payload(metafetcher: MetaFetcher, elbv2_target_groups: list[dict]):
    for resource_details_type in metafetcher.subresources_metadata_types:
        if resource_details_type != "elbv2_target_health":
            continue

        parent_filters = []
        metadata_config = metafetcher.metadata_config(metadata_type="elbv2_target_health")
        assert metadata_config
        filter_key = metadata_config["parent_required_filters"]["filter_key"]
        parent_field_name = metadata_config["parent_required_filters"]["parent_filter_field"]

        for resource in elbv2_target_groups[:2]:
            parent_filters.append({filter_key: resource[parent_field_name]})

        assert len(parent_filters) == 2

        resources = metafetcher.fetch(metadata_type="ecs_clusters", region_name="us-west-2", required_filters=parent_filters)
        for detail in resources:
            assert detail
            assert isinstance(detail, dict)


def test_meta_fetcher_custom_kwargs(metafetcher: MetaFetcher, ec2_instances):

    assert ec2_instances
    assert isinstance(ec2_instances, list)

    resources_list = []

    ec2_instances = ec2_instances[:2]

    for instance in ec2_instances:
        assert isinstance(instance, dict)
        instance_id = instance["InstanceId"]
        custom_kwargs = {"InstanceIds": [instance_id]}
        resources = metafetcher.fetch(metadata_type="ec2_instances", region_name="us-west-2", custom_kwargs=custom_kwargs)
        assert resources

        for r in resources:
            assert isinstance(r, dict)
            resources_list.append(r["InstanceId"])
            assert r["InstanceId"] == instance_id

    assert len(resources_list) == len(ec2_instances)
