from domino.testing import piece_dry_run
import base64
import json


def test_httprequest_get_multiple():
    input_data = {
        'requests': [
            {'url': 'https://jsonplaceholder.typicode.com/posts', 'method': 'GET'},
            {'url': 'https://jsonplaceholder.typicode.com/users', 'method': 'GET'},
        ],
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


def test_httprequest_mixed_methods():
    """Each request can have its own method and body."""
    input_data = {
        'requests': [
            {
                'url': 'https://httpbin.org/post',
                'method': 'POST',
                'body_json_data': json.dumps({'k': 'post-value'}),
            },
            {
                'url': 'https://httpbin.org/put',
                'method': 'PUT',
                'body_json_data': json.dumps({'k': 'put-value'}),
            },
            {
                'url': 'https://httpbin.org/delete',
                'method': 'DELETE',
            },
        ],
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    base64_list = piece_output['base64_bytes_data_list']
    assert len(base64_list) == 3

    post_resp = json.loads(base64.decodebytes(base64_list[0].encode('utf-8')))
    assert post_resp['json']['k'] == 'post-value'

    put_resp = json.loads(base64.decodebytes(base64_list[1].encode('utf-8')))
    assert put_resp['json']['k'] == 'put-value'

    delete_resp = json.loads(base64.decodebytes(base64_list[2].encode('utf-8')))
    assert delete_resp['url'] == 'https://httpbin.org/delete'


def test_httprequest_per_request_bearer_token():
    """Bearer token is per-request and optional."""
    input_data = {
        'requests': [
            {
                'url': 'https://httpbin.org/headers',
                'method': 'GET',
                'bearer_token': 'token-A',
            },
            {
                'url': 'https://httpbin.org/headers',
                'method': 'GET',
            },
        ],
    }
    piece_output = piece_dry_run(
        piece_name="HttpRequestPiece",
        input_data=input_data
    )
    base64_list = piece_output['base64_bytes_data_list']
    assert len(base64_list) == 2

    with_token = json.loads(base64.decodebytes(base64_list[0].encode('utf-8')))
    without_token = json.loads(base64.decodebytes(base64_list[1].encode('utf-8')))
    assert with_token['headers'].get('Authorization') == 'Bearer token-A'
    assert 'Authorization' not in without_token['headers']
