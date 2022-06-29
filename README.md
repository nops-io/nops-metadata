
# nops-metadata
Package allows to pull metadata for AWS entities. List of entities can be found here: [constants](nops_metadata/constants.py)  
For advanced usage see:
- [Sub-resources ingestion](wiki/subresources.md)

Library also provides schemas for all supported metadata producers.
  

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
        spark_schema = fetcher.schema(metadata_type=metadata_type)
        pydantic_model = fetcher.schema(metadata_type=metadata_type, schema_type="pydantic")
