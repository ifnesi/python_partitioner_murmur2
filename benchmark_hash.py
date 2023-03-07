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

import os
import time
import zlib
import string
import random
import hashlib
import murmurhash2

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from functools import partial


# Global variables
KEY_MIN_CHARS = 4
KEY_MAX_CHARS = 32
ROUNDS = 25
MAX_KEYS = 100000
PARTITIONS = 24  # to calculate distribution histogram
FOLDER_HISTOGRAM = "histograms"
HASHING_FUNCTIONS = {
    "murmur2": partial(murmurhash2.murmurhash2, seed=0x9747B28C),
    "murmur3": partial(murmurhash2.murmurhash3, seed=0x9747B28C),
    "crc32": zlib.crc32,
    "adler": zlib.adler32,
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha384": hashlib.sha384,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}

results = dict()
partition_distribution = dict()
for i in range(ROUNDS):
    print(f"Round #{i + 1}/{ROUNDS}:")
    print(f" - Generating {MAX_KEYS} keys...")
    keys = tuple(
        "".join(
            random.choices(
                string.printable,
                k=random.randint(
                    KEY_MIN_CHARS,
                    KEY_MAX_CHARS,
                ),
            )
        ).encode()
        for _ in range(MAX_KEYS)
    )
    for h, f in HASHING_FUNCTIONS.items():
        if i == 0:
            results[h] = 0
            partition_distribution[h] = list()
        print(f" - Generating hashes for {h.strip('.')}")
        hash_list = list()
        start = time.time()
        for key in keys:
            hash_list.append(f(key))
        stop = time.time()
        print(f" - Calculating partitions for {h.strip('.')}")
        for hash in hash_list:
            if isinstance(hash, int):
                partition_distribution[h].append(hash % PARTITIONS)
            else:
                partition_distribution[h].append(int(hash.hexdigest(), 16) % PARTITIONS)
        results[h] += MAX_KEYS / (stop - start)

print("\nResults:")
results_df = pd.DataFrame(results.values(), results.keys())
results_df[0] = results_df[0] / (1000 * ROUNDS)
results_df = results_df.sort_values(0)
print(results_df[0])

# Save results to file
sns.set_style("white")
plt.bar(results_df.index, results_df[0])
plt.title(f"Comparison between Hash functions (Thousand keys/sec)")
plt.xticks(rotation=-90)
plt.grid()
plt.tight_layout()
plt.savefig(
    os.path.join(FOLDER_HISTOGRAM, f"_results.png"),
)
plt.close()

# Generate histograms
print("Generating histograms...")
if not os.path.exists(FOLDER_HISTOGRAM):
    os.mkdir(FOLDER_HISTOGRAM)
df = pd.DataFrame(partition_distribution)
for col in partition_distribution.keys():
    print(f" - {col}", end="")
    value_counts = df[col].value_counts().sort_index()
    # Calculate chi-square
    chi_square = 0
    for j in range(PARTITIONS):
        chi_square += value_counts[j] * (value_counts[j] + 1) / 2
    chi_square /= (ROUNDS * MAX_KEYS / (2 * PARTITIONS)) * (
        ROUNDS * MAX_KEYS + 2 * PARTITIONS - 1
    )
    print(f", Chi-square = {chi_square:.4f}")
    # Save histogram to file
    plt.bar(
        range(PARTITIONS),
        value_counts,
    )
    plt.title(f"{col} (Chi Square: {chi_square:.4f})")
    plt.xticks(range(PARTITIONS))
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(FOLDER_HISTOGRAM, f"{col}.png"))
    plt.close()
