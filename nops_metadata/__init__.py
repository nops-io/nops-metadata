from typing import Any
from typing import Iterator

import boto3
from pyrsistent import freeze
from pyrsistent import thaw

from .constants import METAMAP
from .constants import SINLE_REGION_SERVICES
from .schema import SparkAWSSchemaSerializer
from .utils import resource_listing

METAMAP_DETAILS = freeze(
    {
        "ecs_clusters_details": {
            "fetch_method": "describe_clusters",
            "parameter_name": "clusters",
            "response_key": "clusters",
            "metadata_type": "ecs_clusters",
            "listing_key": "clusterArns",
            "kwargs": {"include": ["ATTACHMENTS", "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"]},
        }
    }
)


class MetaFetcher:
    def __init__(self, session: boto3.Session):
        self.session: boto3.Session = session

    def metadata_regions(self, metadata_type: str) -> list[str]:
        service_name = metadata_type.split("_")[0]
        if service_name in SINLE_REGION_SERVICES:
            return ["us-east-1"]
        else:
            return self.session.get_available_regions(service_name=service_name)

    def schema(self, metadata_type: str) -> dict[str, Any]:
        serializer = SparkAWSSchemaSerializer()
        schema = serializer.schema(metadata_type)
        return schema

    def postgres_schema(self, metadata_type: str) -> dict[str, Any]:
        postgres_custom_types = {
            "string": "varchar",
            "long": "integer",
            "double": "float",
        }
        serializer = SparkAWSSchemaSerializer(custom_types=postgres_custom_types)
        schema = serializer.schema(metadata_type)
        return schema

    @property
    def metadata_types(self) -> list[str]:
        return list(METAMAP.keys())

    def metadata_subtypes(self, metadata_type: str) -> list[str]:
        response = []
        for key, value in METAMAP_DETAILS.items():
            if value["metadata_type"] == metadata_type:
                response.append(key)

        return response

    def fetch(self, metadata_type: str, region_name: str) -> Iterator[dict[str, Any]]:
        return resource_listing(
            session=self.session,
            metaname=metadata_type,
            fetch_method=METAMAP[metadata_type]["fetch_method"],
            response_key=METAMAP[metadata_type]["response_key"],
            page_key=METAMAP[metadata_type].get("page_key", ""),
            call_kwargs=thaw(METAMAP[metadata_type].get("kwargs", {})),
            region_name=region_name,
        )

    def fetch_resources(self, metadata_subtype: str, region_name: str, resources: dict) -> list[dict[str, Any]]:
        fetch_method: str = METAMAP_DETAILS[metadata_subtype]["fetch_method"]  # type: ignore
        parameter_name = METAMAP_DETAILS[metadata_subtype]["parameter_name"]
        response_key = METAMAP_DETAILS[metadata_subtype]["response_key"]
        call_kwargs = thaw(METAMAP_DETAILS[metadata_subtype].get("kwargs", {}))
        listing_key = METAMAP_DETAILS[metadata_subtype]["listing_key"]

        service = metadata_subtype.split("_")[0]
        client_kwargs = {}
        if region_name:
            client_kwargs["region_name"] = region_name

        client = self.session.client(service, **client_kwargs)

        if listing_key:
            resource_kwargs = {parameter_name: resources.get(listing_key)}
        else:
            resource_kwargs = {parameter_name: resources}

        response = getattr(client, fetch_method)(**call_kwargs, **resource_kwargs)[response_key]
        return response
