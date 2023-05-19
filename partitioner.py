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

# Requirements: python3 -m pip install murmurhash2==0.2.10


import zlib
import random
import argparse
import murmurhash2


class Partitioner:
    """
    Implements a partitioner which selects the target partition based on
    the hash of the key. Attempts to apply the same hashing
    function as mainline java (murmur2) or librdkafka (crc32 by default) clients.
    """

    def __init__(self) -> None:
        # Binary multiplication by 0x7FFFFFFF to make it a positive number as the murmur2 hash yields a signed int
        self._murmur2factor = 0x7FFFFFFF

        # Same seed used by Apache Kafka when murmur2 hashing
        # https://github.com/apache/kafka/blob/0.8.2/clients/src/main/java/org/apache/kafka/common/utils/Utils.java#LL246C28-L246C28
        self._murmur2seed = 0x9747B28C

    def get_partition(
        self,
        key: bytes,
        partitions: int,
        partitioner: str = "murmur2",
    ) -> int:
        if key is None:
            # Return random partiton in case key is NULL (None)
            hash = int(random.random() * 999999999999999)
        else:
            if not isinstance(key, bytes):
                key = f"{key}".encode("utf-8")
            if partitioner == "murmur2":
                hash = self._murmur2(key, self._murmur2seed) & self._murmur2factor
            elif partitioner == "crc32":
                hash = self._crc32(key)
            else:
                raise ValueError("Valid partitioners are: murmur2 and crc32")
        return hash % partitions

    def _crc32(
        self,
        data: bytes,
    ) -> int:
        return zlib.crc32(data)

    def _murmur2(
        self,
        data: bytes,
        seed: int,
    ) -> int:
        return murmurhash2.murmurhash2(
            data,
            seed,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get the partition number using either murmur2 (default on Apache Kafka Java lib) or crc32 (default librdkafka lib) hashing functions"
    )
    parser.add_argument(
        "--partitions",
        dest="partitions",
        type=int,
        help="Number of partitions on topic (default 6)",
        default=6,
    )
    parser.add_argument(
        "--key",
        dest="key",
        type=str,
        help="Message key (string, it will be UTF-8 encoded)",
        default=None,
    )
    parser.add_argument(
        "--partitioner",
        dest="partitioner",
        help=f"Set partitioner (default: murmur2)",
        type=str,
        choices=["murmur2", "crc32"],
        default="murmur2",
    )
    args = parser.parse_args()

    p = Partitioner()
    print(
        f"{args.partitioner} hashing key '{args.key}' for a topic with {args.partitions} partitions yields:"
    )
    partition = p.get_partition(
        args.key,
        args.partitions,
        partitioner=args.partitioner,
    )
    print(f" - Partition #: {partition}")
