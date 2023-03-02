import logging
import requests


def delivery_callback(err, msg):
    """Delivery callback for the kafka producer"""
    if err:
        logging.error(f"Message failed delivery for key '{msg.key().decode()}': {err}")
    else:
        logging.debug(
            f"Message key '{msg.key().decode()}' delivered to topic '{msg.topic()}', partition #{msg.partition()}, offset #{msg.offset()}"
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
):
    """Submit HTTP POST request to ksqlDB"""
    try:
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
                    "ksql.streams.auto.offset.reset": "earliest",
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
