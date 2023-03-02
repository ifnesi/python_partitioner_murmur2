# -*- coding: utf-8 -*-
#
# Copyright 2022 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys
import json
import socket
import logging
import argparse
import subprocess
import pandas as pd

from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic

from utils import UserData, delivery_callback, ksqldb, http_request
from utils.murmur2 import Murmur2Partitioner


# Global variables
DEFAULT_TOPIC = "demo_user"
DEFAULT_PARTITIONS = 6
DEFAULT_MESSAGES = 10
DEFAULT_BOOTSTRAP_SERVER = "localhost:9092"
DEFAULT_KSQLDB_ENDPOINT = "http://localhost:8088"
KSQLDB_PUSH_QUERY_OUTPUT = "push_query_output.txt"
keys_validate = dict()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Produce messages using murmur2_random as the partitioner"
    )
    parser.add_argument(
        "--topic",
        dest="topic",
        type=str,
        help=f"Topic name (default '{DEFAULT_TOPIC}')",
        default=DEFAULT_TOPIC,
    )
    parser.add_argument(
        "--partitions",
        dest="partitions",
        type=int,
        help=f"Number of partitions to be set when creating the topic (default is {DEFAULT_PARTITIONS})",
        default=DEFAULT_PARTITIONS,
    )
    parser.add_argument(
        "--messages",
        dest="messages",
        type=int,
        help=f"Number of messages to be produced (default is {DEFAULT_MESSAGES})",
        default=DEFAULT_MESSAGES,
    )
    parser.add_argument(
        "--client_id",
        dest="client_id",
        type=str,
        help=f"Producer Client ID (default is your hostname)",
        default=socket.gethostname(),
    )
    parser.add_argument(
        "--crc32",
        dest="crc32",
        help=f"Set librdkafka's default partitioner (crc32), otherwise it will be used murmur2_random",
        action="store_true",
    )
    parser.add_argument(
        "--bootstrap_server",
        dest="bootstrap_server",
        type=str,
        help=f"Bootstrap servers (default is '{DEFAULT_BOOTSTRAP_SERVER}')",
        default=DEFAULT_BOOTSTRAP_SERVER,
    )
    parser.add_argument(
        "--ksqldb_endpoint",
        dest="ksqldb_endpoint",
        type=str,
        help=f"ksqlDB endpoint (default is '{DEFAULT_KSQLDB_ENDPOINT}')",
        default=DEFAULT_KSQLDB_ENDPOINT,
    )
    parser.add_argument(
        "--debug",
        dest="log_level_debug",
        help=f"Set logging level to debug",
        action="store_true",
    )
    args = parser.parse_args()

    # Set logging
    logging.basicConfig(
        format=f"%(levelname)s %(asctime)s.%(msecs)03d - %(message)s",
        level=logging.DEBUG if args.log_level_debug else logging.INFO,
        datefmt="%H:%M:%S",
    )

    # Validate access to ksqlDB
    print("")
    logging.info(f"Validating access to ksqlDB: {args.ksqldb_endpoint}...")
    status_code, response = http_request(args.ksqldb_endpoint, method="GET")
    if status_code != 200:
        sys.exit(0)

    # Set Kafka config
    kafka_config = {
        "bootstrap.servers": args.bootstrap_server,
        "client.id": args.client_id,
    }

    # Instantiate custom partitioner murmur2 random
    custom_partitioner = Murmur2Partitioner()

    # Create topic if not created already
    ksqldb_topic = f"{args.topic}_orders".replace("-", "_")
    ksqldb_merged = f"{args.topic}_orders_merged".replace("-", "_")
    kafka_admin_client = AdminClient(kafka_config)

    print("")
    logging.info(f"Creating topics: {args.topic} and {ksqldb_topic}...")
    for topic in [args.topic, ksqldb_topic]:
        if dict(kafka_admin_client.list_topics().topics).get(topic) is None:
            kafka_admin_client.create_topics(
                [
                    NewTopic(
                        topic,
                        args.partitions,
                        1,
                    )
                ]
            )

    # Create ksqlDB stream/table
    print("")
    logging.info(f"Creating ksqlDB Stream: {ksqldb_topic}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE STREAM IF NOT EXISTS {ksqldb_topic} (
                user_id VARCHAR KEY,
                ts BIGINT,
                product_id BIGINT,
                qty BIGINT,
                unit_price DOUBLE,
                channel VARCHAR
            ) WITH (
                kafka_topic='{ksqldb_topic}',
                VALUE_FORMAT='JSON',
                timestamp = 'ts'
            );""",
    )

    print("")
    logging.info(f"Creating ksqlDB Table: {args.topic}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE TABLE IF NOT EXISTS {args.topic} (
                user_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                age BIGINT
            ) WITH (
                kafka_topic='{args.topic}',
                VALUE_FORMAT='JSON'
            );""",
    )

    print("")
    logging.info(f"Creating ksqlDB Stream: {ksqldb_merged}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE STREAM IF NOT EXISTS {ksqldb_merged} AS
            SELECT
                DEMO_USER_ORDERS.user_id AS user_id,
                DEMO_USER.name,
                DEMO_USER.age,
                product_id,
                qty,
                unit_price,
                channel,
                ts
            FROM DEMO_USER_ORDERS
            LEFT JOIN DEMO_USER ON DEMO_USER_ORDERS.user_id = DEMO_USER.user_id
        EMIT CHANGES;""",
    )

    # Get number of partitions available on the topic (just in case the topic was previously created with a different number of partitions)
    partitions = len(
        kafka_admin_client.list_topics(args.topic).topics.get(args.topic).partitions
    )

    # Produce data to topics
    print("")
    logging.info(f"Producing messages to topics: {args.topic} and {ksqldb_topic}...")
    producer = Producer(kafka_config)
    user_data = UserData()
    initial_ts = None
    for n in range(args.messages):
        try:
            user_id, user = user_data.generate_user()
            user_id_bytes = user_id.encode()
            producer_config = {
                "key": user_id_bytes,
                "value": json.dumps(user).encode(),
                "callback": delivery_callback,
            }
            if not args.crc32:
                # Set partition using murmur2_random partitioner
                # To use the default lidrbkafka partitioner (crc32) comment out the partition argument below
                producer_config["partition"] = custom_partitioner.partition(
                    user_id_bytes,
                    partitions,
                )

            # Produce data to kafka broker
            producer.produce(
                args.topic,
                **producer_config,
            )

            # Produce data to ksqlDB stream
            order = user_data.generate_user_order()
            if initial_ts is None:
                initial_ts = order["ts"]
            ksqldb(
                args.ksqldb_endpoint,
                f"""INSERT INTO {ksqldb_topic} (
                        user_id,
                        ts,
                        product_id,
                        qty,
                        unit_price,
                        channel
                    ) VALUES (
                        '{user_id}',
                        {order["ts"]},
                        {order["product_id"]},
                        {order["qty"]},
                        {order["unit_price"]},
                        '{order["channel"]}'
                    );""",
            )

        except BufferError:
            logging.error(
                f"Local producer queue is full ({len(producer)} message(s) awaiting delivery): try again"
            )

        except Exception as err:
            logging.error(f"General error when producing key '{user_id}': {err}")

        finally:
            # Async delivery
            producer.poll(0)

    producer.flush()

    # Check partitions on topic and stream
    print("")
    logging.info("Comparing partitions between producer and ksqlDB stream...")
    kafka_config.pop("client.id")
    kafka_config.update(
        {
            "enable.auto.commit": True,
            "group.id": args.client_id,
            "session.timeout.ms": 6000,
            "auto.offset.reset": "earliest",
            "enable.auto.offset.store": True,
        }
    )
    consumer = Consumer(kafka_config)
    consumer.subscribe(
        [
            args.topic,
            ksqldb_topic,
        ]
    )

    # Read messages from Kafka
    no_messages_count = 10
    try:
        while no_messages_count > 0:
            msg = consumer.poll(timeout=0.5)
            if msg is None:
                no_messages_count -= 1
            elif msg.error():
                raise print(msg.error())
            else:
                if msg.topic() not in keys_validate.keys():
                    keys_validate[msg.topic()] = dict()
                keys_validate[msg.topic()][msg.key().decode()] = msg.partition()

    except Exception as err:
        logging.error(f"{err}")

    finally:
        # Close down consumer to commit final offsetsand leave consumer group
        consumer.close()
        # Print results
        total_keys = len(keys_validate.get(args.topic))
        matched_keys = 0
        partition_exceptions = {
            "USER_ID": dict(),
            args.topic: dict(),
            ksqldb_topic: dict(),
        }
        row = 0
        for key, partition in keys_validate.get(args.topic).items():
            partition_ksqldb = keys_validate.get(ksqldb_topic, dict()).get(key)
            if partition_ksqldb is None:
                total_keys -= 1
            elif partition == partition_ksqldb:
                matched_keys += 1
            else:
                partition_exceptions["USER_ID"][row] = key
                partition_exceptions[args.topic][row] = partition
                partition_exceptions[ksqldb_topic][row] = partition_ksqldb
                row += 1
        logging.info(
            f"Matched partitions: {100 * matched_keys / (1 if total_keys <= 0 else total_keys):.2f}%"
        )
        if row > 0:
            logging.info("Partition exceptions:")
            df = pd.DataFrame(partition_exceptions).sort_values(by="USER_ID")
            print(df.to_string(index=False))

        print("")
        logging.info("Push query results on Stream/Table join...")

        ksqldb_endpoint = args.ksqldb_endpoint.replace(
            "127.0.0.1",
            "ksqldb-server",
        ).replace(
            "localhost",
            "ksqldb-server",
        )
        stdout, _ = subprocess.Popen(
            f"""./ksqldb.sh {ksqldb_endpoint} {ksqldb_merged} {initial_ts} {args.messages}""".split(
                " "
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()

        headers = list()
        stream_data = dict()
        row = 0
        for item in re.findall(
            "(\{.+?\})", stdout.decode().replace("\n", " ").replace("\r", " ")
        ):
            try:
                data = json.loads(item)
            except Exception:
                data = dict()
            if "schema" in data.keys() and "queryId" in data.keys():
                for key in re.findall("`(.+?)`", data["schema"]):
                    headers.append(key)
                    stream_data[key] = dict()
            elif "columns" in data.keys():
                for n, i in enumerate(data["columns"]):
                    stream_data[headers[n]][row] = "???" if i is None else str(i)
                row += 1

        df = pd.DataFrame(stream_data).drop("TS", axis=1).sort_values(by="USER_ID")
        print(df.to_string(index=False))
