
# metadata_producer
Package allows to easily pull metadata for various AWS entities.
This module also provides Spark schemas for boto3 responses.
  


**Installation**

    pip install nops-metadata

**Usage**:

Pulling data:

    import boto3
    from nops_metadata import MetaFetcher
    
    fetcher = MetaFetcher(session=boto3.Session())
    for metadata_type in fetcher.metadata_types:
        for region in fetcher.metadata_regions(metadata_type=metadata_type):
            resources = fetcher.fetch(metadata_type=metadata_type, region_name=region)

Getting schemas:

    import boto3
    from metadata_producer import MetaFetcher
    
    fetcher = MetaFetcher(session=boto3.Session())
    for metadata_type in fetcher.metadata_types:
        schema = fetcher.schema(metadata_type=metadata_type)
