from domino.base_piece import BasePiece
from .models import InputModel, OutputModel, RequestItem
import requests
import base64
import json


class HttpRequestPiece(BasePiece):

    def _execute(self, item: RequestItem) -> bytes:
        headers = {}
        if item.bearer_token:
            headers['Authorization'] = f'Bearer {item.bearer_token}'

        body_data = None
        if item.method in ("POST", "PUT") and item.body_json_data.strip():
            try:
                body_data = json.loads(item.body_json_data)
            except json.JSONDecodeError:
                raise Exception(f"Invalid JSON body for {item.url}")

        try:
            if item.method == "GET":
                response = requests.get(item.url, headers=headers)
            elif item.method == "POST":
                response = requests.post(item.url, headers=headers, json=body_data)
            elif item.method == "PUT":
                response = requests.put(item.url, headers=headers, json=body_data)
            elif item.method == "DELETE":
                response = requests.delete(item.url, headers=headers)
            else:
                raise Exception(f"Unsupported HTTP method: {item.method}")
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"HTTP request error for {item.url}: {e}")

        return response.content

    def piece_function(self, input_data: InputModel):
        base64_bytes_data_list = []
        total = len(input_data.requests)
        for index, item in enumerate(input_data.requests):
            self.logger.info(f"Requesting [{index + 1}/{total}] {item.method} {item.url}")
            content = self._execute(item)
            base64_bytes_data_list.append(
                base64.b64encode(content).decode('utf-8')
            )

        return OutputModel(base64_bytes_data_list=base64_bytes_data_list)
