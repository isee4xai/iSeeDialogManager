import json
import requests


def request(url, _params, _headers):
    response = requests.get(url, params=_params, headers=_headers)
    json_res = json.loads(response.text)

    return json_res