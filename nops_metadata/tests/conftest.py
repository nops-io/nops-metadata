import boto3
import pytest

from nops_metadata import MetaFetcher


@pytest.fixture
def aws_session() -> boto3.Session:
    return boto3.Session()


@pytest.fixture()
def metafetcher(aws_session) -> MetaFetcher:
    return MetaFetcher(session=aws_session)
