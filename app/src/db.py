import json
import os
from typing import Any

from influxdb import InfluxDBClient


def setupDb():
    # setup database
    host = os.environ.get('INFLUXDB_HOST', '127.0.0.1')
    user = os.environ.get('INFLUXDB_ADMIN_USER', 'admin')
    password = os.environ.get('INFLUXDB_ADMIN_PASSWORD', 'password')

    client = InfluxDBClient(host, 8086, user, password, 'db')
    client.create_database('db')
    client.get_list_database()  # show the existing databases
    client.switch_database('db')
    client.create_retention_policy(
        "temperatureRetention", duration="1d", replication=1, database='db', default=True)
    return client


def storeFromDictTemp(dictTemp: dict):
    json_payload = []
    client = setupDb()
    to_store = {
        "measurement": "data",
        "tags": {
            "printer": "test"

        },
        "fields": {
            "T_N": dictTemp["NozleTemp"],
            "T_Ngoal": dictTemp["GoalTempNozle"],
            "T_B": dictTemp["TempBed"],
            "T_Bgoal": dictTemp["TempGoalBed"],
            "T_A": dictTemp["TempAir"]
        }
    }
    json_payload.append(to_store)
    client.write_points(json_payload)
