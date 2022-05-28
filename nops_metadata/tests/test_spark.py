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
