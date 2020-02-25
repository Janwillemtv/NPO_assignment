"""Example data producer"""
import json
import requests


for line in open('noisy_mock_events', 'r'):
    line_dict = json.loads(line)

    url = 'http://localhost:6066/event/create/'

    response = requests.post(url, json=line_dict)

    print(response.text)
