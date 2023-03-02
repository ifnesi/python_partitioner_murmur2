import os
import time
import random
import logging
import hashlib
import requests


class UserData:
    def __init__(self):
        self._first_name = self._read_user_data("user_first_name.txt")
        self._last_name = self._read_user_data("user_last_name.txt")
        self._channels = [
            "web",
            "store",
            "partner",
            "catalog",
        ]

    def _read_user_data(
        self,
        file: str,
    ) -> list:
        return [
            item.strip()
            for item in open(os.path.join("utils", file), "r").readlines()
            if item.strip()
        ]

    def _generate_user_id(self, user_name: str) -> str:
        return hashlib.md5(user_name.encode()).hexdigest()

    def generate_user_order(
        self,
    ) -> dict:
        return {
            "ts": int(time.time() * 1000),
            "product_id": random.randint(1000, 1999),
            "qty": random.randint(1, 10),
            "unit_price": int(random.random() * 10000) / 100,
            "channel": random.choice(self._channels),
        }

    def generate_user(
        self,
    ) -> tuple:
        user_name = " ".join(
            [
                random.choice(self._first_name),
                random.choice(self._last_name),
            ]
        )
        user_id = self._generate_user_id(user_name)
        return (
            user_id,
            {
                "name": user_name,
                "age": 18
                + int(user_id[-8:], 16)
                % 50,  # hash name to get same age for the same name
            },
        )


def delivery_callback(err, msg):
    """Delivery callback for the kafka producer"""
    if err:
        logging.error(f"Message failed delivery for key '{msg.key().decode()}': {err}")
    else:
        logging.debug(
            f"Message '{msg.key().decode()} | {msg.value().decode()}' delivered to topic '{msg.topic()}', partition #{msg.partition()}, offset #{msg.offset()}"
        )


def http_request(
    url: str,
    headers: dict = None,
    payload: dict = None,
    method: str = "POST",
) -> tuple:
    """Generic HTTP request"""
    if method == "GET":
        session = requests.get
    elif method == "PUT":
        session = requests.put
    elif method == "PATCH":
        session = requests.patch
    elif method == "DELETE":
        session = requests.delete
    else:
        session = requests.post
    try:
        response = session(
            url,
            headers=headers,
            json=payload,
        )
        return (response.status_code, response.text)
    except requests.exceptions.Timeout:
        logging.error(f"Unable to send request to '{url}': timeout")
        return (408, {err})
    except requests.exceptions.TooManyRedirects:
        logging.error(f"Unable to send request to '{url}': too many redirects")
        return (302, {err})
    except Exception as err:
        logging.error(f"Unable to send request to '{url}': {err}")
        return (500, {err})


def ksqldb(
    end_point: str,
    statement: str,
    offset_reset_earliest: bool = True,
):
    """Submit HTTP POST request to ksqlDB"""
    try:
        # Clean-up statement
        statement = statement.replace("\r", " ")
        statement = statement.replace("\t", " ")
        statement = statement.replace("\n", " ")
        while statement.find("  ") > -1:
            statement = statement.replace("  ", " ")

        url = f"{end_point.strip('/')}/ksql"
        status_code, response = http_request(
            url,
            headers={
                "Accept": "application/vnd.ksql.v1+json",
                "Content-Type": "application/vnd.ksql.v1+json; charset=utf-8",
            },
            payload={
                "ksql": statement,
                "streamsProperties": {
                    "ksql.streams.auto.offset.reset": "earliest"
                    if offset_reset_earliest
                    else "latest",
                    "ksql.streams.cache.max.bytes.buffering": "0",
                },
            },
        )
        if status_code == 200:
            logging.debug(f"ksqlDB ({status_code}): {statement}")
        else:
            raise Exception(f"{response} (Status code {status_code})")
    except Exception as err:
        logging.error(f"Unable to send request to '{url}': {err}")
