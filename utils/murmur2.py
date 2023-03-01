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

# Adapted from https://kafka-python.readthedocs.io/en/1.3.5/_modules/kafka/partitioner/hashed.html
import random


class Murmur2Partitioner:
    """
    Implements a partitioner which selects the target partition based on
    the hash of the key. Attempts to apply the same hashing
    function as mainline java client.
    """

    def partition(
        self,
        key: bytes,
        partitions: int,
    ) -> int:
        # https://github.com/apache/kafka/blob/0.8.2/clients/src/main/java/org/apache/kafka/clients/producer/internals/Partitioner.java#L69
        # Binary multiplication by 0x7FFFFFFF to make it a positive number
        if key is None:
            # Emulate murmur2_random partitioner
            return int(random.random() * 999999999999999) % partitions
        else:
            return (self._murmur2(key) & 0x7FFFFFFF) % partitions

    def _murmur2(
        self,
        data: bytes,
    ) -> int:
        """Pure-python Murmur2 implementation
        Based on java client, see org.apache.kafka.common.utils.Utils.murmur2
        Args:
            data (bytes): opaque bytes
        Returns: MurmurHash2 of data
        """
        length = len(data)
        seed = 0x9747B28C
        # 'm' and 'r' are mixing constants generated offline.
        # They're not really 'magic', they just happen to work well.
        m = 0x5BD1E995
        r = 24

        # Initialize the hash to a random value
        h = seed ^ length
        length4 = length // 4

        for i in range(length4):
            i4 = i * 4
            k = (
                (data[i4 + 0] & 0xFF)
                + ((data[i4 + 1] & 0xFF) << 8)
                + ((data[i4 + 2] & 0xFF) << 16)
                + ((data[i4 + 3] & 0xFF) << 24)
            )
            k &= 0xFFFFFFFF
            k *= m
            k &= 0xFFFFFFFF
            k ^= (k % 0x100000000) >> r  # k ^= k >>> r
            k &= 0xFFFFFFFF
            k *= m
            k &= 0xFFFFFFFF

            h *= m
            h &= 0xFFFFFFFF
            h ^= k
            h &= 0xFFFFFFFF

        # Handle the last few bytes of the input array
        extra_bytes = length % 4
        if extra_bytes >= 3:
            h ^= (data[(length & ~3) + 2] & 0xFF) << 16
            h &= 0xFFFFFFFF
        if extra_bytes >= 2:
            h ^= (data[(length & ~3) + 1] & 0xFF) << 8
            h &= 0xFFFFFFFF
        if extra_bytes >= 1:
            h ^= data[length & ~3] & 0xFF
            h &= 0xFFFFFFFF
            h *= m
            h &= 0xFFFFFFFF

        h ^= (h % 0x100000000) >> 13  # h >>> 13;
        h &= 0xFFFFFFFF
        h *= m
        h &= 0xFFFFFFFF
        h ^= (h % 0x100000000) >> 15  # h >>> 15;
        h &= 0xFFFFFFFF

        return h


if __name__ == "__main__":
    p = Murmur2Partitioner()
    topic_partitions = 6
    print(f"Topic with {topic_partitions} partition(s):")

    partitions_count = dict()
    for i in range(1000):
        partition = p.partition(f"{i:03}".encode(), topic_partitions)
        print(f"Event content '{i:03}' -> partition #{partition}")
        partitions_count[partition] = partitions_count.get(partition, 0) + 1

    print("\nPartitions distribution:")
    for k, v in sorted(partitions_count.items()):
        print(f"#{k}: {v} event(s)")
