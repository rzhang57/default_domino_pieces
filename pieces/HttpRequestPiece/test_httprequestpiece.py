from domino.testing import piece_dry_run
import base64
import json


def test_httprequest_get():
    input_data = {
        'urls': [
            'https://jsonplaceholder.typicode.com/posts',
            'https://jsonplaceholder.typicode.com/users',
        ],
        'method': 'GET'
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    base64_list = piece_output['base64_bytes_data_list']
    assert isinstance(base64_list, list)
    assert len(base64_list) == 2
    for encoded in base64_list:
        decoded = base64.decodebytes(encoded.encode('utf-8'))
        parsed = json.loads(decoded)
        assert isinstance(parsed, list)


def test_httprequest_post():
    input_data = {
        'urls': ['https://httpbin.org/post'],
        'method': 'POST',
        'body_json_data': json.dumps({
            'key_1': 'domino',
            'key_2': 'testing-post'
        })
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    base64_list = piece_output['base64_bytes_data_list']
    assert len(base64_list) == 1
    decoded = base64.decodebytes(base64_list[0].encode('utf-8'))
    parsed = json.loads(decoded)
    assert parsed['json']['key_1'] == 'domino'
    assert parsed['json']['key_2'] == 'testing-post'


def test_httprequest_put():
    input_data = {
        'urls': ['https://httpbin.org/put'],
        'method': 'PUT',
        'body_json_data': json.dumps({
            'key_1': 'domino',
            'key_2': 'testing-put'
        })
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    base64_list = piece_output['base64_bytes_data_list']
    assert len(base64_list) == 1
    decoded = base64.decodebytes(base64_list[0].encode('utf-8'))
    parsed = json.loads(decoded)
    assert parsed['json']['key_1'] == 'domino'
    assert parsed['json']['key_2'] == 'testing-put'


def test_httprequest_delete():
    input_data = {
        'urls': ['https://httpbin.org/delete'],
        'method': 'DELETE'
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    base64_list = piece_output['base64_bytes_data_list']
    assert len(base64_list) == 1
    decoded = base64.decodebytes(base64_list[0].encode('utf-8'))
    parsed = json.loads(decoded)
    assert parsed['url'] == 'https://httpbin.org/delete'
