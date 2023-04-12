# python_partitioner_murmur2
There is no common partitioner amongst Apache Kafka resources/libs/clients. For example all producers using librdkafka by default uses `crc32` (such as Python’s confluent_kafka), whilst Java ones uses `murmur2_random` (Kafka Streams, ksqlDB, Source Connectors, etc.):
> The default partitioner in Java producer uses the murmur2 hash function while the default partitioner in librdkafka uses crc32. Because of the different hash functions, a message produced by a Java client and a message produced by a librdkafka client may be assigned to different partitions even with the same partition key (source: https://docs.confluent.io/kafka-clients/librdkafka/current/overview.html#synchronous-writes).

So, if a producer using python (confluent_kafka/libdrdkafka, for example) and Source Connector (Java) are producing data to Kafka, then very likely a merge on ksqlDB would not work properly as there would be a partition mismatch.<br><br>
This demo features a python script that can use either crc32 or murmu2_random as the partitioner. It will produce messages both to the topic `demo_user` (as set when running the python script) as well as to a ksqlDB stream and have it stored on the topic `demo_user_orders`.

## Demo diagram
![image](docs/demo_diagram.png)

## ksqlDB Table and Streams
### Table `DEMO_USER`
Directly derived from the topic `demo_user` (data produced via python script using either crc32 or murmur2 partitioners)
```
CREATE TABLE IF NOT EXISTS DEMO_USER (
    user_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    age BIGINT
) WITH (
    kafka_topic='demo_user',
    VALUE_FORMAT='JSON'
)
```

### Table `DEMO_USER_REPARTITION`
Materialised from the table `DEMO_USER`, that is to do repartition and force the use of ksqlDB's default partitioner murmur2
```
CREATE TABLE IF NOT EXISTS demo_user_repartition
WITH (
    kafka_topic='demo_user_repartition',
    VALUE_FORMAT='JSON'
)
AS
SELECT
    user_id, name, age
FROM DEMO_USER
EMIT CHANGES;
```

### Stream `demo_user_orders`
Stream fed directly via ksqlDB's REST API (murmur2)
```
CREATE STREAM IF NOT EXISTS demo_user_orders (
    user_id VARCHAR KEY,
    ts BIGINT,
    product_id BIGINT,
    qty BIGINT,
    unit_price DOUBLE,
    channel VARCHAR
) WITH (
    kafka_topic='demo_user_orders',
    VALUE_FORMAT='JSON',
    timestamp = 'ts'
)
```

### Stream `DEMO_USER_ORDERS_MERGED`
Merge `demo_user_orders` stream (murmur2) with table `demo_user` (crc32 or murmur2)
```
CREATE STREAM IF NOT EXISTS DEMO_USER_ORDERS_MERGED AS
    SELECT
        demo_user_orders.user_id AS user_id,
        demo_user.name,
        demo_user.age,
        product_id,
        qty,
        unit_price,
        channel,
        ts
    FROM demo_user_orders
    LEFT JOIN demo_user ON demo_user_orders.user_id = demo_user.user_id
EMIT CHANGES
```

### Stream `DEMO_USER_ORDERS_MERGED_REPARTITION`
Merge `demo_user_orders` stream (murmur2) with table `demo_user_repartition` (murmur2)
```
CREATE STREAM IF NOT EXISTS DEMO_USER_ORDERS_MERGED_REPARTITION AS
    SELECT
        demo_user_orders.user_id AS user_id,
        demo_user_repartition.name,
        demo_user_repartition.age,
        product_id,
        qty,
        unit_price,
        channel,
        ts
    FROM demo_user_orders
    LEFT JOIN demo_user_repartition ON demo_user_orders.user_id = demo_user_repartition.user_id
EMIT CHANGES
```

## Installation and Configuration
- Docker Desktop and Python +3.8 required
- Install python virtual environment: `python3 -m pip install venv`
- Clone this repo: `git clone git@github.com:ifnesi/python_partitioner_murmur2.git`
- Go to the folder where the repo was cloned: `cd python_partitioner_murmur2`
- Create a virtual environment: `python3 -m venv _venv`
- Activate the virtual environment: `source _venv/bin/activate`
- Install project requirements: `python3 -m pip install -f requirements.txt`
- Deactivate the virtual environment: `deactivate`

## Python script usage
```
usage: producer.py [-h]
                  [--topic TOPIC]
                  [--partitions PARTITIONS]
                  [--messages MESSAGES]
                  [--client_id CLIENT_ID]
                  [--bootstrap_server BOOTSTRAP_SERVER]
                  [--partitioner {murmur2_random,murmur2,consistent_random,consistent,fnv1a_random,fnv1a,random}]
                  [--c3_endpoint C3_ENDPOINT]
                  [--ksqldb_endpoint KSQLDB_ENDPOINT]
                  [--debug]

Produce messages using crc32 (consistent_random) or murmur2 (murmur2_random) as the partitioner

options:
  -h, --help            show this help message and exit
  --topic TOPIC         Topic name (default 'demo_user')
  --partitions PARTITIONS
                        Number of partitions to be set when creating the topic (default is 6)
  --messages MESSAGES   Number of messages to be produced (default is 10)
  --client_id CLIENT_ID
                        Producer Client ID (default is your hostname)
  --bootstrap_server BOOTSTRAP_SERVER
                        Bootstrap servers (default is 'localhost:9092')
  --partitioner {murmur2_random,murmur2,consistent_random,consistent,fnv1a_random,fnv1a,random}
                        Set partitioner (default: murmur2_random)
  --c3_endpoint C3_ENDPOINT
                        C3 endpoint (default is 'http://localhost:9021')
  --ksqldb_endpoint KSQLDB_ENDPOINT
                        ksqlDB endpoint (default is 'http://localhost:8088')
  --debug               Set logging level to debug
```

## Running the demo
- Activate the virtual environment: `source _venv/bin/activate`
- Start up docker compose: `docker-compose up -d`
- Waiting around 5 minutes until you can access C3 and it is shown as healthy `http://127.0.0.1:9021/` and the ksqlDB cluster is up `http://127.0.0.1:8088/`
- Running python script (using murmur2_random partitioner): `python3 producer.py --messages 10`
```
INFO 11:47:23.261 - Validating access to: http://localhost:9021...

INFO 11:47:23.296 - Validating access to: http://localhost:8088...

INFO 11:47:23.340 - Creating ksqlDB Table (if not exists): DEMO_USER...

INFO 11:47:23.366 - Creating ksqlDB Table (if not exists): DEMO_USER_REPARTITION...

INFO 11:47:23.410 - Creating ksqlDB Stream (if not exists): DEMO_USER_ORDERS...

INFO 11:47:23.435 - Creating ksqlDB Stream (if not exists): DEMO_USER_ORDERS_MERGED...

INFO 11:47:23.527 - Creating ksqlDB Stream (if not exists): DEMO_USER_ORDERS_MERGED_REPARTITION...

INFO 11:47:23.624 - Producing messages to topics: 'demo_user' (Python Producer) and 'demo_user_orders' (ksqlDB REST API)...

INFO 11:47:23.628 - demo_user: b1d1cff59a5f2751ac3253d25b4bc53b | {"name": "Luella Clements", "age": 65}
INFO 11:47:23.922 - demo_user_orders: b1d1cff59a5f2751ac3253d25b4bc53b | {"ts": 1677844043886, "product_id": 1669, "qty": 6, "unit_price": 68.67, "channel": "store"}

INFO 11:47:23.922 - demo_user: bb867da60ddb05a208297bbfb88d6a3f | {"name": "Jolie Valentine", "age": 37}
INFO 11:47:24.212 - demo_user_orders: bb867da60ddb05a208297bbfb88d6a3f | {"ts": 1677844044183, "product_id": 1151, "qty": 7, "unit_price": 87.76, "channel": "partner"}

INFO 11:47:24.212 - demo_user: b8f38627e83b28d94875723aeca0a02f | {"name": "Adriel Pratt", "age": 61}
INFO 11:47:24.493 - demo_user_orders: b8f38627e83b28d94875723aeca0a02f | {"ts": 1677844044465, "product_id": 1045, "qty": 7, "unit_price": 51.03, "channel": "web"}

INFO 11:47:24.493 - demo_user: 931f7a829152ad9796d5334879bcbe81 | {"name": "Mauricio Henderson", "age": 41}
INFO 11:47:24.799 - demo_user_orders: 931f7a829152ad9796d5334879bcbe81 | {"ts": 1677844044747, "product_id": 1075, "qty": 5, "unit_price": 84.92, "channel": "store"}

INFO 11:47:24.800 - demo_user: 7769e21ef61694a291a2d6b521a1fdac | {"name": "Taliyah Krueger", "age": 32}
INFO 11:47:25.086 - demo_user_orders: 7769e21ef61694a291a2d6b521a1fdac | {"ts": 1677844045052, "product_id": 1753, "qty": 8, "unit_price": 6.95, "channel": "web"}

INFO 11:47:25.086 - demo_user: 93bff61b7a465190a54d3fc9202890da | {"name": "Keagan Garrett", "age": 52}
INFO 11:47:25.373 - demo_user_orders: 93bff61b7a465190a54d3fc9202890da | {"ts": 1677844045340, "product_id": 1884, "qty": 5, "unit_price": 17.92, "channel": "catalog"}

INFO 11:47:25.373 - demo_user: 39b5d50c216029714e4a132a311d500a | {"name": "Orlando Fernandez", "age": 36}
INFO 11:47:25.661 - demo_user_orders: 39b5d50c216029714e4a132a311d500a | {"ts": 1677844045627, "product_id": 1225, "qty": 10, "unit_price": 75.4, "channel": "catalog"}

INFO 11:47:25.662 - demo_user: 5b18abd5f523210e957f52ccc8fb6f4c | {"name": "Joel O\u2019Donnell", "age": 46}
INFO 11:47:25.963 - demo_user_orders: 5b18abd5f523210e957f52ccc8fb6f4c | {"ts": 1677844045917, "product_id": 1629, "qty": 5, "unit_price": 91.45, "channel": "store"}

INFO 11:47:25.963 - demo_user: 07f538476ed5f9ee6e14a0669aa37573 | {"name": "Jay Yoder", "age": 67}
INFO 11:47:26.254 - demo_user_orders: 07f538476ed5f9ee6e14a0669aa37573 | {"ts": 1677844046216, "product_id": 1029, "qty": 7, "unit_price": 64.93, "channel": "catalog"}

INFO 11:47:26.255 - demo_user: 53980af7bff16580978defb6f4242458 | {"name": "Elina Lara", "age": 22}
INFO 11:47:26.557 - demo_user_orders: 53980af7bff16580978defb6f4242458 | {"ts": 1677844046510, "product_id": 1949, "qty": 9, "unit_price": 71.47, "channel": "web"}

INFO 11:47:26.557 - Comparing partitions between producer (demo_user) and ksqlDB (demo_user_orders)...
INFO 11:47:34.158 - Matched partitions: 100.00%

INFO 11:47:34.158 - Comparing partitions between producer (demo_user_repartition) and ksqlDB (demo_user_orders)...
INFO 11:47:41.732 - Matched partitions: 100.00%

INFO 11:47:41.732 - Push query results on Stream/Table join: DEMO_USER_ORDERS_MERGED
                         USER_ID               NAME AGE PRODUCT_ID QTY UNIT_PRICE CHANNEL
07f538476ed5f9ee6e14a0669aa37573          Jay Yoder  67       1029   7      64.93 catalog
39b5d50c216029714e4a132a311d500a  Orlando Fernandez  36       1225  10       75.4 catalog
53980af7bff16580978defb6f4242458         Elina Lara  22       1949   9      71.47     web
5b18abd5f523210e957f52ccc8fb6f4c     Joel O’Donnell  46       1629   5      91.45   store
7769e21ef61694a291a2d6b521a1fdac    Taliyah Krueger  32       1753   8       6.95     web
931f7a829152ad9796d5334879bcbe81 Mauricio Henderson  41       1075   5      84.92   store
93bff61b7a465190a54d3fc9202890da     Keagan Garrett  52       1884   5      17.92 catalog
b1d1cff59a5f2751ac3253d25b4bc53b    Luella Clements  65       1669   6      68.67   store
b8f38627e83b28d94875723aeca0a02f       Adriel Pratt  61       1045   7      51.03     web
bb867da60ddb05a208297bbfb88d6a3f    Jolie Valentine  37       1151   7      87.76 partner

INFO 11:47:43.571 - Push query results on Stream/Table join: DEMO_USER_ORDERS_MERGED_REPARTITION
                         USER_ID               NAME AGE PRODUCT_ID QTY UNIT_PRICE CHANNEL
07f538476ed5f9ee6e14a0669aa37573          Jay Yoder  67       1029   7      64.93 catalog
39b5d50c216029714e4a132a311d500a  Orlando Fernandez  36       1225  10       75.4 catalog
53980af7bff16580978defb6f4242458         Elina Lara  22       1949   9      71.47     web
5b18abd5f523210e957f52ccc8fb6f4c     Joel O’Donnell  46       1629   5      91.45   store
7769e21ef61694a291a2d6b521a1fdac    Taliyah Krueger  32       1753   8       6.95     web
931f7a829152ad9796d5334879bcbe81 Mauricio Henderson  41       1075   5      84.92   store
93bff61b7a465190a54d3fc9202890da     Keagan Garrett  52       1884   5      17.92 catalog
b1d1cff59a5f2751ac3253d25b4bc53b    Luella Clements  65       1669   6      68.67   store
b8f38627e83b28d94875723aeca0a02f       Adriel Pratt  61       1045   7      51.03     web
bb867da60ddb05a208297bbfb88d6a3f    Jolie Valentine  37       1151   7      87.76 partner
```

- Running python script (using crc32 partitioner): `python3 producer.py --messages 10 --partitioner consistent_random`
```
INFO 11:48:32.965 - Validating access to: http://localhost:9021...

INFO 11:48:32.994 - Validating access to: http://localhost:8088...

INFO 11:48:33.039 - Creating ksqlDB Table (if not exists): DEMO_USER...

INFO 11:48:33.065 - Creating ksqlDB Table (if not exists): DEMO_USER_REPARTITION...

INFO 11:48:33.100 - Creating ksqlDB Stream (if not exists): DEMO_USER_ORDERS...

INFO 11:48:33.125 - Creating ksqlDB Stream (if not exists): DEMO_USER_ORDERS_MERGED...

INFO 11:48:33.213 - Creating ksqlDB Stream (if not exists): DEMO_USER_ORDERS_MERGED_REPARTITION...

INFO 11:48:33.305 - Producing messages to topics: 'demo_user' (Python Producer) and 'demo_user_orders' (ksqlDB REST API)...

INFO 11:48:33.307 - demo_user: b7eb209cde19021de8ee60524a313eba | {"name": "Destiney Bernal", "age": 24}
INFO 11:48:33.596 - demo_user_orders: b7eb209cde19021de8ee60524a313eba | {"ts": 1677844113565, "product_id": 1249, "qty": 8, "unit_price": 0.13, "channel": "partner"}

INFO 11:48:33.596 - demo_user: b07398f4d618333e241ab3f34e99c1dd | {"name": "Maximo Manning", "age": 53}
INFO 11:48:33.890 - demo_user_orders: b07398f4d618333e241ab3f34e99c1dd | {"ts": 1677844113850, "product_id": 1997, "qty": 5, "unit_price": 78.85, "channel": "partner"}

INFO 11:48:33.890 - demo_user: 111c123c95fdc24603f9fef28862a117 | {"name": "Jonathon Montoya", "age": 61}
INFO 11:48:34.192 - demo_user_orders: 111c123c95fdc24603f9fef28862a117 | {"ts": 1677844114148, "product_id": 1584, "qty": 1, "unit_price": 9.08, "channel": "store"}

INFO 11:48:34.192 - demo_user: 31732a0f37acf5cb05f06daf1f827762 | {"name": "Leo Robertson", "age": 56}
INFO 11:48:34.488 - demo_user_orders: 31732a0f37acf5cb05f06daf1f827762 | {"ts": 1677844114448, "product_id": 1497, "qty": 4, "unit_price": 93.78, "channel": "partner"}

INFO 11:48:34.488 - demo_user: 24f7f396cc2a19c36eefe8b424085bdc | {"name": "Sonny Ewing", "age": 48}
INFO 11:48:34.777 - demo_user_orders: 24f7f396cc2a19c36eefe8b424085bdc | {"ts": 1677844114745, "product_id": 1585, "qty": 9, "unit_price": 89.31, "channel": "store"}

INFO 11:48:34.777 - demo_user: a9b83b707a9d7144e56665dc633fc389 | {"name": "Alexandra Johnston", "age": 27}
INFO 11:48:35.076 - demo_user_orders: a9b83b707a9d7144e56665dc633fc389 | {"ts": 1677844115032, "product_id": 1759, "qty": 7, "unit_price": 1.62, "channel": "catalog"}

INFO 11:48:35.076 - demo_user: 70d38d0a6dfc05506fc647be7eb1a9aa | {"name": "Catalina Holden", "age": 40}
INFO 11:48:35.372 - demo_user_orders: 70d38d0a6dfc05506fc647be7eb1a9aa | {"ts": 1677844115332, "product_id": 1160, "qty": 8, "unit_price": 95.35, "channel": "store"}

INFO 11:48:35.372 - demo_user: 71d301d7701b9971340d3595942619e6 | {"name": "Mariana Kirby", "age": 34}
INFO 11:48:35.664 - demo_user_orders: 71d301d7701b9971340d3595942619e6 | {"ts": 1677844115625, "product_id": 1039, "qty": 8, "unit_price": 83.92, "channel": "catalog"}

INFO 11:48:35.664 - demo_user: 9e6debacf13e7ea560c77ece2c0c5039 | {"name": "Valentin Harris", "age": 41}
INFO 11:48:35.969 - demo_user_orders: 9e6debacf13e7ea560c77ece2c0c5039 | {"ts": 1677844115917, "product_id": 1933, "qty": 9, "unit_price": 81.49, "channel": "partner"}

INFO 11:48:35.969 - demo_user: 8684f69ede86d8607ddd899e2a0612e0 | {"name": "Ember Bowman", "age": 38}
INFO 11:48:36.279 - demo_user_orders: 8684f69ede86d8607ddd899e2a0612e0 | {"ts": 1677844116226, "product_id": 1329, "qty": 1, "unit_price": 46.67, "channel": "catalog"}

INFO 11:48:36.279 - Comparing partitions between producer (demo_user) and ksqlDB (demo_user_orders)...
INFO 11:48:43.872 - Matched partitions: 20.00%
INFO 11:48:43.872 - Partition exceptions:
                         USER_ID  demo_user  demo_user_orders
111c123c95fdc24603f9fef28862a117          0                 3
24f7f396cc2a19c36eefe8b424085bdc          2                 1
70d38d0a6dfc05506fc647be7eb1a9aa          1                 5
8684f69ede86d8607ddd899e2a0612e0          3                 1
9e6debacf13e7ea560c77ece2c0c5039          5                 1
a9b83b707a9d7144e56665dc633fc389          2                 4
b07398f4d618333e241ab3f34e99c1dd          2                 4
b7eb209cde19021de8ee60524a313eba          2                 0

INFO 11:48:43.877 - Comparing partitions between producer (demo_user_repartition) and ksqlDB (demo_user_orders)...
INFO 11:48:51.466 - Matched partitions: 100.00%

INFO 11:48:51.466 - Push query results on Stream/Table join: DEMO_USER_ORDERS_MERGED
                         USER_ID          NAME AGE PRODUCT_ID QTY UNIT_PRICE CHANNEL
111c123c95fdc24603f9fef28862a117           ??? ???       1584   1       9.08   store
24f7f396cc2a19c36eefe8b424085bdc           ??? ???       1585   9      89.31   store
31732a0f37acf5cb05f06daf1f827762 Leo Robertson  56       1497   4      93.78 partner
70d38d0a6dfc05506fc647be7eb1a9aa           ??? ???       1160   8      95.35   store
71d301d7701b9971340d3595942619e6 Mariana Kirby  34       1039   8      83.92 catalog
8684f69ede86d8607ddd899e2a0612e0           ??? ???       1329   1      46.67 catalog
9e6debacf13e7ea560c77ece2c0c5039           ??? ???       1933   9      81.49 partner
a9b83b707a9d7144e56665dc633fc389           ??? ???       1759   7       1.62 catalog
b07398f4d618333e241ab3f34e99c1dd           ??? ???       1997   5      78.85 partner
b7eb209cde19021de8ee60524a313eba           ??? ???       1249   8       0.13 partner

INFO 11:48:53.193 - Push query results on Stream/Table join: DEMO_USER_ORDERS_MERGED_REPARTITION
                         USER_ID               NAME AGE PRODUCT_ID QTY UNIT_PRICE CHANNEL
111c123c95fdc24603f9fef28862a117   Jonathon Montoya  61       1584   1       9.08   store
24f7f396cc2a19c36eefe8b424085bdc        Sonny Ewing  48       1585   9      89.31   store
31732a0f37acf5cb05f06daf1f827762      Leo Robertson  56       1497   4      93.78 partner
70d38d0a6dfc05506fc647be7eb1a9aa    Catalina Holden  40       1160   8      95.35   store
71d301d7701b9971340d3595942619e6      Mariana Kirby  34       1039   8      83.92 catalog
8684f69ede86d8607ddd899e2a0612e0       Ember Bowman  38       1329   1      46.67 catalog
9e6debacf13e7ea560c77ece2c0c5039    Valentin Harris  41       1933   9      81.49 partner
a9b83b707a9d7144e56665dc633fc389 Alexandra Johnston  27       1759   7       1.62 catalog
b07398f4d618333e241ab3f34e99c1dd     Maximo Manning  53       1997   5      78.85 partner
b7eb209cde19021de8ee60524a313eba    Destiney Bernal  24       1249   8       0.13 partner
```
- Once done with it, stop your docker containers: `docker-compose down`
- Deactivate the virtual environment: `deactivate`