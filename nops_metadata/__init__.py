import logging
from threading import Thread
from typing import Any
from typing import Iterator
from typing import Optional
from datetime import datetime

import boto3
from pyrsistent import thaw

from .constants import METAMAP
from .constants import SUBRESOURCES_METAMAP
from .constants import SINLE_REGION_SERVICES
from .schema import PydanticSchemaGenerator
from .spark_schema import SparkAWSSchemaSerializer
from .utils import resource_listing
from queue import Empty
from typing import List
from queue import Queue


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
        return (METAMAP | SUBRESOURCES_METAMAP)[metadata_type]

    @property
    def metadata_types(self) -> list[str]:
        return list(METAMAP.keys())

    @property
    def subresources_metadata_types(self) -> list[str]:
        return list(SUBRESOURCES_METAMAP.keys())

    def fetch_in_threads(
        self,
        metadata_config: dict,
        call_kwargs: dict,
        metadata_type: str,
        region_name: str,
        num_threads: int,
        required_filters: Optional[list[dict[str, Any]]] = None,
    ):
        kwargs_list = []
        for filter_kwargs in required_filters or []:
            kwargs_list.append(dict(call_kwargs, **filter_kwargs))

        def _worker():
            while True:
                try:
                    task_kwargs = task_queue.get(block=False)
                    resources = resource_listing(
                        session=self.session,
                        metaname=metadata_type,
                        fetch_method=metadata_config["fetch_method"],
                        response_key=metadata_config.get("response_key"),
                        page_key=metadata_config.get("page_key", ""),
                        call_kwargs=task_kwargs,
                        region_name=region_name,
                    )
                    queue.put(list(resources), timeout=60 * 3)

                # Ends worker life.
                except Empty:
                    break

                except Exception as e:
                    pass

        task_queue: Queue = Queue(maxsize=len(kwargs_list))
        queue: Queue = Queue(maxsize=len(kwargs_list))

        for kwarg in kwargs_list:
            task_queue.put(kwarg)

        threads: List[Thread] = [Thread(target=_worker) for _ in range(num_threads)]

        for thread in threads:
            thread.start()

        while True:
            try:
                yield from queue.get(block=True, timeout=5)

            except Empty:
                any_alive = any([thread.is_alive() for thread in threads])
                if not any_alive:
                    break

    def fetch(self, metadata_type: str, region_name: str, required_filters: Optional[list[dict[str, Any]]] = None, custom_kwargs: Optional[dict[str, Any]] = None, num_threads: int = 5) -> Iterator[dict[str, Any]]:
        metadata_config = self.metadata_config(metadata_type)
        call_kwargs = thaw(metadata_config.get("kwargs", {}))

        try:
            if "parent_required_filters" in metadata_config:
                yield from self.fetch_in_threads(
                    metadata_config=metadata_config,
                    call_kwargs=call_kwargs,
                    metadata_type=metadata_type,
                    region_name=region_name,
                    required_filters=required_filters,
                    num_threads=num_threads,
                )
            else:
                yield from resource_listing(
                    session=self.session,
                    metaname=metadata_type,
                    fetch_method=metadata_config["fetch_method"],
                    response_key=metadata_config.get("response_key"),
                    page_key=metadata_config.get("page_key", ""),
                    call_kwargs=custom_kwargs or call_kwargs,
                    region_name=region_name,
                )
        except Exception as e:
            logging.exception(f"[{datetime.now()}] metadata_producer {region_name} region fetch error: {e}", exc_info=False)
            yield from iter([])
