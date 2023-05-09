# make request to localhost:6060/api/organization/get_key with X-Shared-Secret header
import os

import requests


def get_key(team_id):
    url = f"http://localhost:6060/api/organization/get_key/{team_id}"
    headers = {"X-Shared-Secret": os.environ["API_SHARED_SECRET"]}
    response = requests.get(url=url, headers=headers)
    print("response: ", response.json())
    return response.json()["key"]