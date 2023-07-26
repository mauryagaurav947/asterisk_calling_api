import requests
import json


def api_call():
    response = requests.get(
        "http://192.168.1.11:8000/demo?machine_number=192.168.1.50")

    if response.status_code == 200:
        json_response = json.loads(response.text)

        print(json_response["id"])


if __name__ == "__main__":
    api_call()
