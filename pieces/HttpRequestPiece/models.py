from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class MethodTypes(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class RequestItem(BaseModel):
    url: str = Field(
        description="URL to make a request to.",
    )
    method: MethodTypes = Field(
        default=MethodTypes.GET,
        description="HTTP method to use for this request.",
    )
    bearer_token: str = Field(
        default="",
        description="Optional bearer token for authentication.",
    )
    body_json_data: str = Field(
        default="",
        description="JSON body for POST/PUT requests. Leave blank for none.",
        json_schema_extra={
            'widget': "codeeditor-json",
        }
    )


class InputModel(BaseModel):
    requests: List[RequestItem] = Field(
        default=[RequestItem(url="")],
        description="List of HTTP requests to perform. Each entry has its own URL, method, bearer token, and body.",
    )


class OutputModel(BaseModel):
    base64_bytes_data_list: List[str] = Field(
        description='Output data as a list of base64 encoded strings, one per request.'
    )
