from string import capwords
from typing import Any
from typing import Iterator

import boto3
from botocore.paginate import Paginator
from pyrsistent import thaw


def _extract_keyed_page(page: dict, page_key: str, response_key: str) -> Iterator[dict[str, Any]]:
    keyed_page = page[page_key]

    if isinstance(keyed_page, dict):
        for element in keyed_page.get(response_key, []):
            yield element
    else:
        for section in keyed_page:
            for element in section[response_key]:
                yield element


def _handle_page(page: dict, page_key: str, response_key: str) -> Iterator[dict[str, Any]]:
    page_iter = (
        page[response_key]
        if not page_key
        else list(_extract_keyed_page(page, page_key=page_key, response_key=response_key))
    )

    if isinstance(page_iter, list):
        if page_iter and isinstance(page_iter[0], str):
            yield {response_key: page_iter}
        else:
            for element in page_iter:
                yield element
    else:
        if isinstance(page_iter, str):
            yield {response_key: page_iter}
        else:
            yield page_iter


def resource_listing(
    session: boto3.Session,
    metaname: str,
    fetch_method: str,
    response_key: str,
    page_key: str,
    call_kwargs: dict[str, Any],
    region_name: str,
) -> Iterator[dict]:
    service = metaname.split("_")[0]
    client_kwargs = {}
    if region_name:
        client_kwargs["region_name"] = region_name

    client = session.client(service, **client_kwargs)

    if client.can_paginate(fetch_method):
        paginator: Paginator = client.get_paginator(fetch_method)

        for page in paginator.paginate(**thaw(call_kwargs)):
            for element in _handle_page(page=page, page_key=page_key, response_key=response_key):
                yield element
    else:
        response: list[dict] = getattr(client, fetch_method)(**call_kwargs)[response_key]
        if isinstance(response, list):
            for el in response:
                yield el
        else:
            yield response
