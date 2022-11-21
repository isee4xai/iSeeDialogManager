import json
import requests


def request(url, params):
    response = requests.get(url, params=params)
    json_res = json.loads(response.text)

    return json_res