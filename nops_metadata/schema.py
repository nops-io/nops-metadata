from datetime import datetime
from typing import Any
from typing import Optional

from botocore import xform_name
from botocore.loaders import Loader
from botocore.model import ServiceModel
from pydantic import BaseModel
from pydantic import create_model

from .constants import METAMAP

loader = Loader()


class PydanticSchemaGenerator:
    def __init__(
        self,
        custom_types: Optional[dict] = None,
    ):
        self.custom_types = custom_types or {}
        self.type_store = {}

    def schema(self, metadata_type: str = "ec2_instances"):
        self.type_store = {}  # Reset type store to avoid conflicts with other schemas.
        service = metadata_type.split("_")[0]
        operation_name: Any = METAMAP[metadata_type]["fetch_method"]

        json_service_model = loader.load_service_model(service_name=service, type_name="service-2")
        sm = ServiceModel(json_service_model, service_name=service)

        mapping = {}
        for op_name in sm.operation_names:  # type: ignore
            py_operation_name = xform_name(op_name)
            mapping[py_operation_name] = op_name

        operation_model = sm.operation_model(mapping[operation_name])
        shape = operation_model.output_shape
        return self._get_shape_and_return_schema(shape=shape, metadata_type=metadata_type)

    def _get_shape_and_return_schema(
        self,
        shape,
        metadata_type,
    ):
        page_key = METAMAP[metadata_type].get("page_key")
        response_key: Any = METAMAP[metadata_type]["response_key"]

        if page_key:
            inner_response = shape.members[page_key]

            if inner_response.type_name == "structure":
                response_shape = inner_response.members[response_key].member
            elif inner_response.type_name == "list":
                response_shape = inner_response.member.members[response_key].member
            else:
                raise ValueError(shape)

            return self.parse(shape=response_shape, name=page_key)

        else:
            inner_response = shape.members[response_key]

            if inner_response.type_name == "list":
                response_shape = inner_response.member
            else:
                response_shape = inner_response

            if response_shape.type_name in ["string"]:
                field = self.parse(inner_response, name=response_key)
                return create_model(inner_response.name, **{inner_response.name: field})

            response = self.parse(response_shape, name=response_key)
            if isinstance(response, tuple):
                return create_model(response_key, **{response_key: response})

            return response

    def _parse_shape_blob(self, shape, name, *args):
        return (bytes, None)

    def _parse_shape_long(self, shape, name, *args):
        return (int, None)

    def _parse_shape_double(self, shape, name, *args):
        return (float, None)

    def _parse_shape_float(self, shape, name, *args):
        return (float, None)

    def _parse_shape_map(self, shape, name, *args):
        return (dict, None)

    def _parse_shape_integer(self, shape, name, *args):
        return (int, None)

    def _parse_shape_boolean(self, shape, name, *args):
        return (bool, None)

    def _parse_shape_string(self, shape, name, *args):
        return (str, None)

    def _parse_shape_timestamp(self, shape, name, *args):
        return (datetime, None)

    def _parse_shape_list(self, shape, name, previous_shape_name):
        array_type = self.parse(shape=shape.member, name=name, previous_shape_name=previous_shape_name)
        response = (list[array_type], None)
        return response

    def _parse_shape_structure(self, shape, name, previous_shape_name=""):
        class_attrs = {}
        for key, internal_shape in shape.members.items():
            item = self.parse(shape=internal_shape, name=key, previous_shape_name=name)
            if not isinstance(item, tuple):
                item = (item, None)
            class_attrs[key] = item

        type_name = f"{previous_shape_name}{name}"

        if type_name not in self.type_store:
            self.type_store[type_name] = create_model(f"{previous_shape_name}{name}", **class_attrs)

        response = self.type_store[type_name]
        return response

    def parse(self, shape, name="", previous_shape_name=""):
        return getattr(self, f"_parse_shape_{shape.type_name}")(shape, name, previous_shape_name)
