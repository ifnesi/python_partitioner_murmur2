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

# Some benchmarks about the usage of several hashing functions
# Generate {MAX_KEYS} keys, have them hashed {ROUNDS} times, then calculate the average keys/sec

import time
import zlib
import string
import random
import hashlib
import murmurhash2

from functools import partial


ROUNDS = 25
MAX_KEYS = 100000

m2 = partial(murmurhash2.murmurhash2, seed=0x9747B28C)
m3 = partial(murmurhash2.murmurhash3, seed=0x9747B28C)
hashing_functions = {
    "murmur2": m2,
    "murmur3": m3,
    "crc32..": zlib.crc32,
    "adler..": zlib.adler32,
    "md5....": hashlib.md5,
    "sha1...": hashlib.sha1,
    "sha224.": hashlib.sha224,
    "sha384.": hashlib.sha384,
    "sha256.": hashlib.sha256,
    "sha512.": hashlib.sha512,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}

results = dict()
for i in range(ROUNDS):
    print(f"Round #{i + 1}/{ROUNDS}:")
    print(f"Generating {MAX_KEYS} keys...")
    keys = tuple(
        "".join(
            random.choices(
                string.printable,
                k=random.randint(
                    4,
                    32,
                ),
            )
        ).encode()
        for _ in range(MAX_KEYS)
    )
    for h, f in hashing_functions.items():
        print(f" - Generating hashes for {h.strip('.')}")
        start = time.time()
        for key in keys:
            f(key)
        stop = time.time()
        if i == 0:
            results[h] = 0
        results[h] += MAX_KEYS / (stop - start)

print("\nResults:")
for h, r in sorted(results.items(), key=lambda item: item[1]):
    print(f" - {h}: {r / ROUNDS:.0f} keys/sec")
