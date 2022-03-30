import json
import os
from typing import Any

from influxdb import InfluxDBClient
from datetime import datetime


def setupDb():
    # setup database
    host = os.environ.get('INFLUXDB_HOST', '127.0.0.1')
    user = os.environ.get('INFLUXDB_ADMIN_USER', 'admin')
    password = os.environ.get('INFLUXDB_ADMIN_PASSWORD', 'password')

    client = InfluxDBClient(host, 8086, user, password, 'db')
    client.create_database('dbtemp')
    client.get_list_database()  # show the existing databases
    client.switch_database('dbtemp')
    client.create_retention_policy(
        "tempRetention", duration="1h", replication=1, database='dbtemp', default=True)
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
