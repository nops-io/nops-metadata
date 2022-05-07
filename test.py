import boto3
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

from metadata_producer import MetaFetcher

spark = SparkSession.builder.appName("[lake] kafka->iceberg").getOrCreate()

fetcher = MetaFetcher(session=boto3.Session())
for metadata_type in fetcher.metadata_types:
    schema = fetcher.schema(metadata_type=metadata_type)
    all_resources = []

    for region in fetcher.metadata_regions(metadata_type=metadata_type):
        if region not in ["us-west-2", "us-east-1"]:
            continue

        try:
            resources = fetcher.fetch(
                metadata_type=metadata_type, region_name=region)
            all_resources += [r for r in resources]
            print("SUCCESS", metadata_type, region)

        except Exception as e:
            print("ERROR", metadata_type, region, e)

    spark_schema = StructType.fromJson(schema)

    df = spark.createDataFrame(data=all_resources, schema=spark_schema)
    # with open(f"data/{metadata_type}.csv", "w") as f:
    #     data = df.toPandas().to_csv(index=False)
    #     f.write(data)
