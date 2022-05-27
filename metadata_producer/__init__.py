from typing import Any
from typing import Iterator
from typing import Optional
from pyrsistent import thaw

import boto3

from .constants import METAMAP
from .constants import SINLE_REGION_SERVICES
from .utils import resource_listing
from .schema import SparkAWSSchemaSerializer


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

    def metadata_config(self, metadata_type: str) -> dict[str, Any]:
        return METAMAP[metadata_type]

    @property
    def metadata_types(self) -> list[str]:
        return list(METAMAP.keys())

    def fetch(self, metadata_type: str, region_name: str, extra_kwargs: Optional[dict] = None) -> Iterator[dict[str, Any]]:
        metadata_config = self.metadata_config(metadata_type)
        call_kwargs = thaw(metadata_config.get("kwargs", {}))
        if isinstance(extra_kwargs, dict):
            call_kwargs.update(extra_kwargs)
        return resource_listing(
            session=self.session,
            metaname=metadata_type,
            fetch_method=metadata_config["fetch_method"],
            response_key=metadata_config["response_key"],
            page_key=metadata_config.get("page_key", ""),
            call_kwargs=call_kwargs,
            region_name=region_name,
        )
