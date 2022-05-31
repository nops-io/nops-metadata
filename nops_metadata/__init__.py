from typing import Any
from typing import Iterator
from typing import Optional

import boto3
from pyrsistent import freeze
from pyrsistent import thaw

from .constants import METAMAP
from .constants import SINLE_REGION_SERVICES
from .schema import PydanticSchemaGenerator
from .spark_schema import SparkAWSSchemaSerializer
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

    def schema(self, metadata_type: str, schema_type: str = "spark") -> Any:
        if schema_type == "spark":
            return SparkAWSSchemaSerializer().schema(metadata_type=metadata_type)
        elif schema_type == "pydantic":
            return PydanticSchemaGenerator().schema(metadata_type)
        else:
            raise ValueError(f"{schema_type} is not supported.")

    def postgres_schema(self, metadata_type: str) -> dict[str, Any]:
        postgres_custom_types = {
            "string": "varchar",
            "long": "integer",
            "double": "float",
        }
        serializer = SparkAWSSchemaSerializer(custom_types=postgres_custom_types)
        schema = serializer.schema(metadata_type)
        return schema

    def metadata_config(self, metadata_type: str) -> dict[str, Any]:
        return METAMAP[metadata_type]

    @property
    def metadata_types(self) -> list[str]:
        return list(METAMAP.keys())

    def metadata_subtypes(self, metadata_type: str) -> list[str]:
        response = []
        for key, value in METAMAP_DETAILS.items():
            if value["metadata_type"] == metadata_type:
                response.append(key)

        return response

    def fetch(self, metadata_type: str, region_name: str, required_filters: Optional[list[dict[str, Any]]] = None) -> Iterator[dict[str, Any]]:
        metadata_config = self.metadata_config(metadata_type)
        call_kwargs = thaw(metadata_config.get("kwargs", {}))
        kwargs_list = []

        if "parent_required_filters" in metadata_config:
            for filter_kwargs in (required_filters or []):
                kwargs_list.append(dict(call_kwargs, **filter_kwargs))
        else:
            kwargs_list.append(call_kwargs)

        for kwargs in kwargs_list:
            yield from resource_listing(
                session=self.session,
                metaname=metadata_type,
                fetch_method=metadata_config["fetch_method"],
                response_key=metadata_config["response_key"],
                page_key=metadata_config.get("page_key", ""),
                call_kwargs=kwargs,
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
