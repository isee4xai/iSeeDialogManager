import json
import requests


def request(url):
    response = requests.get(url)
    json_res = json.loads(response.text)

    return json_res