import logging
from itertools import chain
from pprint import pprint
from uuid import uuid4

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

from nops_metadata import MetaFetcher


def test_spark_schema_output(metafetcher: MetaFetcher):
    spark = SparkSession.builder.appName(f"testing_metafetcher_{uuid4()}").getOrCreate()

    for metadata_type in metafetcher.metadata_types:
        schema = metafetcher.schema(metadata_type=metadata_type)
        spark_schema = StructType.fromJson(schema)
        df = spark.createDataFrame(data=[], schema=spark_schema)
        assert df


def test_pydantic_schema_output(metafetcher: MetaFetcher):
    def _getter(metadata_type, region):
        try:
            for element in metafetcher.fetch(metadata_type=metadata_type, region_name=region):
                yield element
        except Exception as e:
            logging.warning(e)

    for metadata_type in metafetcher.metadata_types:

        # if metadata_type not in debug:
        #     continue

        try:
            regions = metafetcher.metadata_regions(metadata_type=metadata_type)
            regions.insert(0, "us-west-2")

            gens = [_getter(metadata_type, region) for region in regions]
            response = chain(*gens)
            single_resource = next(response)

            schema = metafetcher.schema(metadata_type=metadata_type, schema_type="pydantic")
            processed_item = schema(**single_resource)
            assert schema.schema()["properties"]
            assert processed_item

        except StopIteration:
            pass
