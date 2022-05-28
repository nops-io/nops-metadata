from nops_metadata import MetaFetcher
from nops_metadata import METAMAP
import pytest
import boto3


@pytest.fixture
def aws_session() -> boto3.Session:
    return boto3.Session()


@pytest.fixture()
def metafetcher(aws_session) -> MetaFetcher:
    return MetaFetcher(session=aws_session)


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


def test_meta_fetcher_pulling_resource_details_payload(metafetcher: MetaFetcher, ecs_clusters: list[dict]):
    for resource_details_type in metafetcher.metadata_subtypes(metadata_type="ecs_clusters"):
        for resources in ecs_clusters[:1]:
            resource_details = metafetcher.fetch_resources(
                metadata_subtype=resource_details_type,
                region_name="us-west-2",
                resources=resources,
            )
            assert resource_details
            assert isinstance(resource_details, list)

            for detail in resource_details:
                assert detail
                assert isinstance(detail, dict)


# def test_meta_fetcher_pulling_resource_details_schema(metafetcher: MetaFetcher, ecs_clusters: list[dict]):
#     for metadata_subtype in metafetcher.metadata_subtypes(metadata_type="ecs_clusters"):
#         schema = metafetcher.schema(metadata_subtype=metadata_subtype)
#         assert schema
