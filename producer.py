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

import json
import time
import uuid
import random
import socket
import argparse
import requests

from functools import partial
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic

from utils.murmur2 import Murmur2Partitioner


# Global variables
DEFAULT_TOPIC = "test_topic"
DEFAULT_PARTITIONS = 6
DEFAULT_MESSAGES = 10
DEFAULT_BOOTSTRAP_SERVER = "localhost:9092"
DEFAULT_KSQLDB_ENDPOINT = "http://localhost:8088"
keys_validate = dict()


# General functions
def delivery_callback(verbose, err, msg):
    if err:
        print(f"Message failed delivery for key '{msg.key().decode()}': {err}")
    else:
        if verbose:
            print(
                f"Message key '{msg.key().decode()}' delivered to topic '{msg.topic()}', partition #{msg.partition()}, offset #{msg.offset()}"
            )


def ksqldb(
    end_point: str,
    statement: str,
    verbose: bool = False,
):
    try:
        url = f"{end_point.strip('/')}/ksql"
        response = requests.post(
            url=url,
            headers={
                "Accept": "application/vnd.ksql.v1+json",
                "Content-Type": "application/vnd.ksql.v1+json; charset=utf-8",
            },
            json={
                "ksql": statement,
                "streamsProperties": {
                    "ksql.streams.auto.offset.reset": "earliest",
                    "ksql.streams.cache.max.bytes.buffering": "0",
                },
            },
        )
        if response.status_code == 200:
            if verbose:
                print(f"ksqlDB ({response.status_code}): {statement}")
        else:
            raise Exception(f"{response.text} (Status code {response.status_code})")
    except Exception as err:
        print(f"ERROR Unable to send request to '{url}': {err}")


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
        "--random_keys",
        dest="random_keys",
        help=f"Set keys as random UUIDs",
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
        "--verbose",
        dest="verbose",
        help=f"Display logs",
        action="store_true",
    )
    args = parser.parse_args()

    # Set Kafka config
    kafka_config = {
        "bootstrap.servers": args.bootstrap_server,
        "client.id": args.client_id,
    }

    # Instantiate custom partitioner murmur2 random
    custom_partitioner = Murmur2Partitioner()

    # Create topic if not created already
    kafka_admin_client = AdminClient(kafka_config)
    print(f"Creating topic: {args.topic}...")
    if dict(kafka_admin_client.list_topics().topics).get(args.topic) is None:
        kafka_admin_client.create_topics(
            [
                NewTopic(
                    args.topic,
                    args.partitions,
                    1,
                )
            ]
        )

    # Create ksqlDB stream/topic
    ksqldb_topic = f"{args.topic}_ksql".replace("-", "_")
    print(f"Creating ksqlDB Stream: {ksqldb_topic}...")
    ksqldb(
        args.ksqldb_endpoint,
        f"CREATE STREAM IF NOT EXISTS {ksqldb_topic} (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='{ksqldb_topic}', VALUE_FORMAT='JSON', PARTITIONS={args.partitions}, REPLICAS=1);",
        verbose=args.verbose,
    )

    # Get number of partitions available on the topic (just in case the topic was previously created with a different number of partitions)
    partitions = len(
        kafka_admin_client.list_topics(args.topic).topics.get(args.topic).partitions
    )

    # Produce data to topic
    print(f"Producing messages to topics: {args.topic} and {ksqldb_topic}...")
    delivery_callback_partial = partial(delivery_callback, args.verbose)
    producer = Producer(kafka_config)
    for n in range(args.messages):
        try:
            if args.random_keys:
                key = uuid.uuid4().hex.encode()
            else:
                key = f"{n}".encode()
            key_decoded = key.decode()

            timestamp = int(time.time() * 1000)
            random_value = random.random()
            producer_config = {
                "key": key_decoded,
                "value": json.dumps(
                    {
                        "key": key_decoded,
                        "timestamp": timestamp,
                        "random_value": random_value,
                    }
                ).encode(),
                "callback": delivery_callback_partial,
            }
            if not args.crc32:
                # Set partition using murmur2_random partitioner
                # To use the default lidrbkafka partitioner (crc32) comment out the partition argument below
                producer_config["partition"] = custom_partitioner.partition(
                    key,
                    partitions,
                )

            # Produce data to kafka broker
            producer.produce(
                args.topic,
                **producer_config,
            )

            # Produce data to ksqlDB stream
            ksqldb(
                args.ksqldb_endpoint,
                f"INSERT INTO {ksqldb_topic} (id,key,timestamp,random_value) VALUES ('{key_decoded}','{key_decoded}',{timestamp},{random_value});",
                verbose=args.verbose,
            )

        except BufferError:
            print(
                f"ERROR: Local producer queue is full ({len(producer)} message(s) awaiting delivery): try again"
            )
        except Exception as err:
            print(f"ERROR: General error when producing key '{key_decoded}': {err}")
        finally:
            # Async delivery
            producer.poll(0)

    producer.flush()

    # Check partitions on topic and stream
    print("Comparing partitions between producer and ksqlDB stream...")
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
                raise print(f"ERROR: {msg.error()}")
            else:
                if msg.topic() not in keys_validate.keys():
                    keys_validate[msg.topic()] = dict()
                keys_validate[msg.topic()][msg.key().decode()] = msg.partition()

    except Exception as err:
        print(f"ERROR: {err}")

    finally:
        # Close down consumer to commit final offsetsand leave consumer group
        consumer.close()
        # Print results
        total_keys = len(keys_validate.get(args.topic))
        matched_keys = 0
        exception_keys = list()
        for key, partition in keys_validate.get(args.topic).items():
            partition_ksqldb = keys_validate.get(ksqldb_topic, dict()).get(key)
            if partition == partition_ksqldb:
                matched_keys += 1
            else:
                exception_keys.append(
                    f"Key '{key}': '{args.topic}' = {partition} | '{ksqldb_topic}' = {partition_ksqldb}"
                )
        print(f" - Matched partitions: {100 * matched_keys / total_keys:.2f}%")
        for e in exception_keys:
            print(f" - {e}")
