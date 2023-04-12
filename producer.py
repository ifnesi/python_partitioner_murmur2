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
import time
import socket
import logging
import argparse
import subprocess
import pandas as pd

from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic

from utils import UserData, delivery_callback, ksqldb, http_request


# Global variables
DEFAULT_TOPIC = "demo_user"
DEFAULT_PARTITIONS = 6
DEFAULT_MESSAGES = 10
DEFAULT_BOOTSTRAP_SERVER = "localhost:9092"
DEFAULT_C3_ENDPOINT = "http://localhost:9021"
DEFAULT_KSQLDB_ENDPOINT = "http://localhost:8088"


if __name__ == "__main__":
    PARTITIONERS = [
        "murmur2_random",
        "murmur2",
        "consistent_random",
        "consistent",
        "fnv1a_random",
        "fnv1a",
        "random",
    ]
    parser = argparse.ArgumentParser(
        description="Produce messages using crc32 (consistent_random) or murmur2 (murmur2_random) as the partitioner"
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
        "--bootstrap_server",
        dest="bootstrap_server",
        type=str,
        help=f"Bootstrap servers (default is '{DEFAULT_BOOTSTRAP_SERVER}')",
        default=DEFAULT_BOOTSTRAP_SERVER,
    )
    parser.add_argument(
        "--partitioner",
        dest="partitioner",
        help=f"Set partitioner (default: {PARTITIONERS[0]})",
        type=str,
        default=PARTITIONERS[0],
        choices=PARTITIONERS,
    )
    parser.add_argument(
        "--c3_endpoint",
        dest="c3_endpoint",
        type=str,
        help=f"C3 endpoint (default is '{DEFAULT_C3_ENDPOINT}')",
        default=DEFAULT_C3_ENDPOINT,
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

    # Validate HTTP access to C3/ksqlDB
    for url in [args.c3_endpoint, args.ksqldb_endpoint]:
        print("")
        logging.info(f"Validating access to: {url}...")
        status_code, response = http_request(args.ksqldb_endpoint, method="GET")
        if status_code != 200:
            sys.exit(0)

    # Set Kafka config
    kafka_config = {
        "bootstrap.servers": args.bootstrap_server,
        "client.id": args.client_id,
        "partitioner": args.partitioner,
    }

    # Create topics if not created already
    topic_user = args.topic
    topic_orders = f"{topic_user}_orders".replace("-", "_")
    topic_user_repartition = f"{topic_user}_repartition".replace("-", "_")

    kafka_admin_client = AdminClient(kafka_config)
    all_topics = dict(kafka_admin_client.list_topics().topics)

    any_topic_created = False
    for topic in [
        topic_user,
        topic_orders,
        topic_user_repartition,
    ]:
        if dict(kafka_admin_client.list_topics().topics).get(topic) is None:
            any_topic_created = True
            print("")
            logging.info(f"Creating topic: {topic}...")
            kafka_admin_client.create_topics(
                [
                    NewTopic(
                        topic,
                        args.partitions,
                        1,
                    )
                ]
            )

    # Create ksqlDB streams/tables
    print("")
    table_user = topic_user.upper()
    logging.info(f"Creating ksqlDB Table (if not exists): {table_user}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE TABLE IF NOT EXISTS {table_user} (
                user_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                age BIGINT
            ) WITH (
                kafka_topic='{topic_user}',
                VALUE_FORMAT='JSON'
            );""",
    )
    if any_topic_created:
        time.sleep(5)

    print("")
    table_user_repartition = topic_user_repartition.upper()
    logging.info(f"Creating ksqlDB Table (if not exists): {table_user_repartition}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE TABLE IF NOT EXISTS {table_user_repartition}
            WITH (
                kafka_topic='{topic_user_repartition}',
                VALUE_FORMAT='JSON'
            )
            AS
            SELECT
                user_id, name, age
            FROM {table_user}
            EMIT CHANGES;""",
    )
    if any_topic_created:
        time.sleep(5)

    print("")
    stream_orders = topic_orders.upper()
    logging.info(f"Creating ksqlDB Stream (if not exists): {stream_orders}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE STREAM IF NOT EXISTS {stream_orders} (
                user_id VARCHAR KEY,
                ts BIGINT,
                product_id BIGINT,
                qty BIGINT,
                unit_price DOUBLE,
                channel VARCHAR
            ) WITH (
                kafka_topic='{topic_orders}',
                VALUE_FORMAT='JSON',
                timestamp = 'ts'
            );""",
    )
    if any_topic_created:
        time.sleep(5)

    print("")
    stream_orders_merged = f"{topic_user}_orders_merged".replace("-", "_").upper()
    logging.info(f"Creating ksqlDB Stream (if not exists): {stream_orders_merged}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE STREAM IF NOT EXISTS {stream_orders_merged} AS
            SELECT
                {stream_orders}.user_id AS user_id,
                {table_user}.name,
                {table_user}.age,
                product_id,
                qty,
                unit_price,
                channel,
                ts
            FROM {stream_orders}
            LEFT JOIN {table_user} ON {stream_orders}.user_id = {table_user}.user_id
        EMIT CHANGES;""",
    )
    if any_topic_created:
        time.sleep(5)

    print("")
    stream_orders_merged_repartition = (
        f"{topic_user}_orders_merged_repartition".replace("-", "_").upper()
    )
    logging.info(
        f"Creating ksqlDB Stream (if not exists): {stream_orders_merged_repartition}..."
    )
    ksqldb(
        args.ksqldb_endpoint,
        f"""CREATE STREAM IF NOT EXISTS {stream_orders_merged_repartition} AS
            SELECT
                {stream_orders}.user_id AS user_id,
                {table_user_repartition}.name,
                {table_user_repartition}.age,
                product_id,
                qty,
                unit_price,
                channel,
                ts
            FROM {stream_orders}
            LEFT JOIN {table_user_repartition} ON {stream_orders}.user_id = {table_user_repartition}.user_id
        EMIT CHANGES;""",
    )
    if any_topic_created:
        time.sleep(5)

    # Get number of partitions available on the topic (just in case the topic was previously created with a different number of partitions)
    partitions = len(
        kafka_admin_client.list_topics(topic_user).topics.get(topic_user).partitions
    )

    # Produce data to topics
    print("")
    logging.info(
        f"Producing messages to topics: '{topic_user}' (Python Producer) and '{topic_orders}' (ksqlDB REST API)..."
    )

    producer = Producer(kafka_config)
    user_data = UserData()
    initial_ts = None
    for n in range(args.messages):
        print("")
        try:
            user_id, user = user_data.generate_user()
            user_id_bytes = user_id.encode()
            producer_config = {
                "key": user_id_bytes,
                "value": json.dumps(user).encode(),
                "callback": delivery_callback,
            }

            # Produce python data to kafka broker
            producer.produce(
                topic_user,
                **producer_config,
            )
            logging.info(f"{topic_user}: {user_id} | {json.dumps(user)}")
            producer.flush()

            # Produce data to ksqlDB stream (REST API)
            time.sleep(
                0.25
            )  # Allow the partitioned table (table_user_repartition) to be sync'ed with the original one (table_user) as it is a derived query
            order = user_data.generate_user_order()
            if initial_ts is None:
                initial_ts = order["ts"]
            ksqldb(
                args.ksqldb_endpoint,
                f"""INSERT INTO {topic_orders} (
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
            logging.info(f"{topic_orders}: {user_id} | {json.dumps(order)}")

        except BufferError:
            logging.error(
                f"Local producer queue is full ({len(producer)} message(s) awaiting delivery): try again"
            )

        except Exception as err:
            logging.error(f"General error when producing key '{user_id}': {err}")

    # Check partitions on topic and stream
    kafka_config.pop("client.id")
    kafka_config.pop("partitioner")
    kafka_config.update(
        {
            "enable.auto.commit": True,
            "session.timeout.ms": 6000,
            "auto.offset.reset": "earliest",
            "enable.auto.offset.store": True,
        }
    )
    for topics in [[topic_user, topic_orders], [topic_user_repartition, topic_orders]]:
        topic_producer = topics[0]
        topic_ksqldb = topics[1]
        kafka_config["group.id"] = f"{args.client_id}_{topic_producer}"

        print("")
        logging.info(
            f"Comparing partitions between producer ({topic_producer}) and ksqlDB ({topic_ksqldb})..."
        )
        consumer = Consumer(kafka_config)
        consumer.subscribe(topics)

        # Read messages from Kafka
        no_messages_count = 15
        keys_validate = dict()
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
            # Close down consumer to commit final offsets and leave consumer group
            consumer.close()

        # Print results
        total_keys = len(keys_validate.get(topic_producer))
        matched_keys = 0
        partition_exceptions = {
            "USER_ID": dict(),
            topic_producer: dict(),
            topic_ksqldb: dict(),
        }
        row = 0
        for key, partition in keys_validate.get(topic_producer).items():
            partition_ksqldb = keys_validate.get(topic_ksqldb, dict()).get(key)
            if partition_ksqldb is None:
                total_keys -= 1
            elif partition == partition_ksqldb:
                matched_keys += 1
            else:
                partition_exceptions["USER_ID"][row] = key
                partition_exceptions[topic_producer][row] = partition
                partition_exceptions[topic_ksqldb][row] = partition_ksqldb
                row += 1
        logging.info(
            f"Matched partitions: {100 * matched_keys / (1 if total_keys <= 0 else total_keys):.2f}%"
        )
        if row > 0:
            logging.info("Partition exceptions:")
            df = pd.DataFrame(partition_exceptions).sort_values(by="USER_ID")
            print(df.to_string(index=False))

    # Compare stream/table join for both tables (python producer and ksqldb repartition)
    for stream in [stream_orders_merged, stream_orders_merged_repartition]:
        print("")
        logging.info(f"Push query results on Stream/Table join: {stream}")

        ksqldb_endpoint = args.ksqldb_endpoint.replace(
            "127.0.0.1",
            "ksqldb-server",
        ).replace(
            "localhost",
            "ksqldb-server",
        )
        stdout, _ = subprocess.Popen(
            f"""./ksqldb.sh {ksqldb_endpoint} {stream} {initial_ts} {args.messages}""".split(
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
