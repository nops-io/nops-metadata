
# Sub-resources fetching
- [Brief overview](#brief-overview)
- [Constants file mapping](#constants-file-mapping)
- [Usage](#usage)

### Brief overview
Some boto3 calls have required keyword arguments. 
<br>For example to ingest S3 bucket versioning info you need to execute `s3_bucket_versioning` and pass kwargs `(Bucket="S3 Bucket Name)`.


### Constants file mapping
To apply sub-resources ingestion you'll need to add your entry to `SUBRESOURCES_METAMAP` that is located in [constants](nops_metadata/constants.py).

Entry example and description:

```python
"NEW_TABLE_NAME": {
    "fetch_method": "get_bucket_versioning",
    "response_key": "LIKE_IN_OTHER_RESOURCE_ENTRIES(OPTIONAL)",
    "parent_required_filters": {
        "filter_key": "KEY_REQUIRED_SEE_BOTO3_DOCS",
        "parent_filter_field": "FIELD_NAME_OF_PARENT_RESOURCE",
        "parent_metadata_type": "s3_buckets",
    }
}
```

Note: `parent_filter_field` will be used to get required filter values from the table specified in `parent_metadata_type`.<br>
For example for `s3_bucket_versioning` parent table is `s3_buckets` and parent value field will be `Name`. So the `required_filter` list value will be:
```python
{"Bucket": "{Name}"}
```


### Usage
To do things like this ^ in this library you'll need to add `required_filters: Optional[list[dict[str, Any]]] = None` argument to `MetaFetcher.fetch` method.

`required_filters` is  a list of arguments that will be applied in for loop for the boto3 method.


Example:
```python
def fetch_s3_versioning(s3_bucket_names: list = []) -> Iterator[dict[str, Any]]
    required_filters = []

    for bucket_name in s3_bucket_names:
        required_filters.append({"Bucket": bucket_name})

    yield from fetcher.fetch(
        metadata_type="s3_bucket_versioning", region_name="us-west-2", required_filters=required_filters
    )
```

Under the hood it will execute `fetch_method` specified in [constants](nops_metadata/constants.py) file for every item in `required_filters` list.
<br>By default it will do that in 5 threads queue, but it can be tuned using `num_threads` keyword argument in `MetaFetcher.fetch()` method.

I won't recommend to use `num_threads` parameter larger than 5 because the limits are not tested on prod yet, `5 threads * 4 region processes * 30 keda workers` may lead to aws throttles our requests or other bad things. 
