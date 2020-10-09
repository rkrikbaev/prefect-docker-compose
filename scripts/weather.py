# A simple example to demonstrate Prefect is working as expected

import os
import json
import time
import requests
import prefect
from prefect import Flow, task, Client

logger = prefect.context.get("logger")

@task
def get_woeid(city: str):
    logger.info("Getting {}'s woeid".format(city))
    api_endpoint = "https://www.metaweather.com/api//location/search/?query={}".format(city)
    response = requests.get(api_endpoint)
    time.sleep(5)
    if response.status_code == 200:
        payload = json.loads(response.text)
        return payload[0]["woeid"]
    else:
        raise("Failed to query " + api_endpoint)

@task
def get_weather(woeid: int):
    logger.info("Getting weather of {}".format(woeid))
    api_endpoint = "https://www.metaweather.com/api/location/{}".format(woeid)
    response = requests.get(api_endpoint)
    time.sleep(5)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise("Failed to query " + api_endpoint)

with Flow("Get Paris' weather") as flow:
    woeid = get_woeid("Paris")
    weather_data = get_weather(woeid)
    logger.debug(weather_data)

try:
    client = Client()
    client.create_project(project_name="weather")
except prefect.utilities.exceptions.ClientError as e:
    logger.info("Project already exists")

flow.register(project_name="weather", labels=["development"])

# Optionaly run the code now
flow.run()