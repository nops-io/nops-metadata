from typing import Any
from typing import Optional

from botocore import xform_name
from botocore.loaders import Loader
from botocore.model import ServiceModel

from .constants import METAMAP

loader = Loader()


spark_type_map = {"structure": "struct", "list": "array"}


class SparkAWSSchemaSerializer:
    def __init__(
        self,
        custom_types: Optional[dict] = None,
    ):
        self.custom_types = custom_types or {}

    def schema(self, metadata_type: str = "ec2_instances"):

        service = metadata_type.split("_")[0]
        operation_name: Any = METAMAP[metadata_type]["fetch_method"]

        # TODO avoid hardcoding service-2
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

            return self.parse(shape=response_shape)

        else:
            inner_response = shape.members[response_key]

            if inner_response.type_name == "list":
                response_shape = inner_response.member
            else:
                response_shape = inner_response

            if response_shape.type_name in ["string", "map"]:
                fields = [self.parse(inner_response, name=response_key)]
                return {
                    "type": "struct",
                    "fields": fields,
                }

            return self.parse(response_shape)

    def _parse_shape_blob(self, shape, name):
        return {
            "name": name,
            "type": "binary",
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_long(self, shape, name):
        return {
            "name": name,
            "type": self.custom_types.get("long", "long"),
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_double(self, shape, name):
        return {
            "name": name,
            "type": self.custom_types.get("double", "double"),
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_float(self, shape, name):
        return {
            "name": name,
            "type": "float",
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_map(self, shape, name):
        return {
            "name": name,
            "type": {
                "type": "map",
                "keyType": shape.key.type_name,
                "valueType": shape.value.type_name,
                "valueContainsNull": True,
            },
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_integer(self, shape, name):
        return {
            "name": name,
            "type": "integer",
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_boolean(self, shape, name):
        return {
            "name": name,
            "type": "boolean",
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_string(self, shape, name):
        output = {
            "name": name,
            "type": self.custom_types.get("string", "string"),
            "nullable": True,
            "metadata": {},
        }

        return output

    def _parse_shape_timestamp(self, shape, name):
        return {
            "name": name,
            "type": "timestamp",
            "nullable": True,
            "metadata": {},
        }

    def _parse_shape_list(self, shape, name):
        if shape.member.type_name not in ["structure", "list"]:
            element_type = shape.member.type_name
        else:
            element_type = self.parse(shape.member)

        output = {
            "type": {
                "type": "array",
                "elementType": element_type,
                "containsNull": True,
            },
            "nullable": True,
            "metadata": {},
            "name": name,
        }

        return output

    def _parse_shape_structure(self, shape, name):
        response = {"type": "struct"}

        if name:
            response["name"] = name

        fields = []

        for key, internal_shape in shape.members.items():
            if internal_shape.type_name not in ["structure", "list"]:
                item = self.parse(internal_shape, name=key)

            elif internal_shape.type_name == "structure":
                item = {"name": key, "type": self.parse(internal_shape), "nullable": True, "metadata": {}}

            elif internal_shape.type_name == "list":
                item = self.parse(shape=internal_shape, name=key)

            else:
                raise ValueError(internal_shape.type_name)

            fields.append(item)

        response["fields"] = fields
        return response

    def parse(self, shape, name=None):
        type_name = shape.type_name
        return getattr(self, f"_parse_shape_{type_name}")(shape, name)
