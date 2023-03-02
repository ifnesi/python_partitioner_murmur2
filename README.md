# python_partitioner_murmur2
There is no common partitioner for all Apache Kafka resources/libs/clients. For example all producers using librdkafka by default uses `crc32` (such as Python’s confluent_kafka), whilst JAVA ones uses `murmur2_random` (Kafka Streams, ksqlDB, Source Connectors, etc.).
> The default partitioner in Java producer uses the murmur2 hash function while the default partitioner in librdkafka uses crc32. Because of the different hash functions, a message produced by a Java client and a message produced by a librdkafka client may be assigned to different partitions even with the same partition key (source: https://docs.confluent.io/kafka-clients/librdkafka/current/overview.html#synchronous-writes).

So, if a producer using python (confluent_kafka lib) and Source Connector are producing data to Kafka, then very likely a merge on ksqlDB would not work properly as there would be a partition mismatch.<br><br>
The python script on this demo can use either crc32 or murmu2_random as the partitioner. It will produce messages both to the topic `{topic}` (as set when running the python script) as well as to a ksqlDB stream and have it stored on the topic `{topic}-ksql`.

```
usage: producer.py [-h]
                   [--topic TOPIC]
                   [--partitions PARTITIONS]
                   [--messages MESSAGES]
                   [--client_id CLIENT_ID]
                   [--crc32]
                   [--random_keys]
                   [--bootstrap_server BOOTSTRAP_SERVER]
                   [--ksqldb_endpoint KSQLDB_ENDPOINT]
                   [--debug]

Produce messages using murmur2_random as the partitioner

options:
  -h, --help            show this help message and exit
  --topic TOPIC         Topic name (default 'test_topic')
  --partitions PARTITIONS
                        Number of partitions to be set when creating the topic (default is 6)
  --messages MESSAGES   Number of messages to be produced (default is 10)
  --client_id CLIENT_ID
                        Producer Client ID (default is your hostname)
  --crc32               Set librdkafka's default partitioner (crc32), otherwise it will be used murmur2_random
  --random_keys         Set keys as random UUIDs
  --bootstrap_server BOOTSTRAP_SERVER
                        Bootstrap servers (default is 'localhost:9092')
  --ksqldb_endpoint KSQLDB_ENDPOINT
                        ksqlDB endpoint (default is 'http://localhost:8088')
  --debug               Set logging level to debug
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

## Running script
- Start up docker compose: `docker-compose up -d`
- Waiting until you can access C3: `http://127.0.0.1:9021/` and the ksqlDB cluster is up: `http://127.0.0.1:8088/`
- Running python script (using murmur2_random partitioner): `python3 producer.py --messages 25 --random_keys --debug`
```
INFO 09:35:02.882 - Validating access to ksqlDB: http://localhost:8088...
DEBUG 09:35:02.887 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:02.904 - http://localhost:8088 "GET / HTTP/1.1" 307 0
DEBUG 09:35:02.908 - http://localhost:8088 "GET /info HTTP/1.1" 200 132

INFO 09:35:02.940 - Creating topic: test_topic...

INFO 09:35:02.948 - Creating ksqlDB Stream: test_topic_ksql...
DEBUG 09:35:02.949 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.205 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 426
DEBUG 09:35:03.206 - ksqlDB (200): CREATE STREAM IF NOT EXISTS test_topic_ksql (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='test_topic_ksql', VALUE_FORMAT='JSON', PARTITIONS=6, REPLICAS=1);

INFO 09:35:03.208 - Producing messages to topics: test_topic and test_topic_ksql...
DEBUG 09:35:03.212 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.449 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.450 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('4f6ac633fe10497ea96ca5600b6b65df','4f6ac633fe10497ea96ca5600b6b65df',1677749703209,0.4998948387627158);
DEBUG 09:35:03.450 - Message key '4f6ac633fe10497ea96ca5600b6b65df' delivered to topic 'test_topic', partition #4, offset #0
DEBUG 09:35:03.454 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.490 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.490 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b2b7c1b9e7774196ac4265ca810be2e6','b2b7c1b9e7774196ac4265ca810be2e6',1677749703451,0.7338778196645284);
DEBUG 09:35:03.490 - Message key 'b2b7c1b9e7774196ac4265ca810be2e6' delivered to topic 'test_topic', partition #4, offset #1
DEBUG 09:35:03.491 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.520 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.520 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('586163f064664dd8b57d5d06fa011429','586163f064664dd8b57d5d06fa011429',1677749703490,0.5860577606939866);
DEBUG 09:35:03.520 - Message key '586163f064664dd8b57d5d06fa011429' delivered to topic 'test_topic', partition #3, offset #0
DEBUG 09:35:03.523 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.554 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.555 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('2bf6f49c538a4edba355e270bc0ffb25','2bf6f49c538a4edba355e270bc0ffb25',1677749703521,0.17166123889665563);
DEBUG 09:35:03.555 - Message key '2bf6f49c538a4edba355e270bc0ffb25' delivered to topic 'test_topic', partition #1, offset #0
DEBUG 09:35:03.556 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.585 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.586 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('97fdc23322b348ac9333f1167090f9af','97fdc23322b348ac9333f1167090f9af',1677749703555,0.1554764098539072);
DEBUG 09:35:03.586 - Message key '97fdc23322b348ac9333f1167090f9af' delivered to topic 'test_topic', partition #3, offset #1
DEBUG 09:35:03.587 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.617 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.618 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('fb5a421ea70a499d976fe6ab90e65bc7','fb5a421ea70a499d976fe6ab90e65bc7',1677749703586,0.006237484848985009);
DEBUG 09:35:03.618 - Message key 'fb5a421ea70a499d976fe6ab90e65bc7' delivered to topic 'test_topic', partition #0, offset #0
DEBUG 09:35:03.619 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.648 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.648 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('28bd3e7a035744ff90fbf6188d95e677','28bd3e7a035744ff90fbf6188d95e677',1677749703618,0.6522878586620645);
DEBUG 09:35:03.648 - Message key '28bd3e7a035744ff90fbf6188d95e677' delivered to topic 'test_topic', partition #4, offset #2
DEBUG 09:35:03.649 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.677 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.677 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c32fd1f8045a405bb622e31a68525f2e','c32fd1f8045a405bb622e31a68525f2e',1677749703648,0.6635538558876878);
DEBUG 09:35:03.677 - Message key 'c32fd1f8045a405bb622e31a68525f2e' delivered to topic 'test_topic', partition #4, offset #3
DEBUG 09:35:03.678 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.741 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.741 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('2f5736bd70c54b36b80b0b548052cdd1','2f5736bd70c54b36b80b0b548052cdd1',1677749703677,0.9820174377834101);
DEBUG 09:35:03.741 - Message key '2f5736bd70c54b36b80b0b548052cdd1' delivered to topic 'test_topic', partition #1, offset #1
DEBUG 09:35:03.742 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.769 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.769 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('747a4ccb4b664f86918e51b0bc744e16','747a4ccb4b664f86918e51b0bc744e16',1677749703741,0.3925805138713211);
DEBUG 09:35:03.770 - Message key '747a4ccb4b664f86918e51b0bc744e16' delivered to topic 'test_topic', partition #2, offset #0
DEBUG 09:35:03.770 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.796 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.796 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('9b4a0070bfa941118e92790ed29fd252','9b4a0070bfa941118e92790ed29fd252',1677749703770,0.7550194458159496);
DEBUG 09:35:03.797 - Message key '9b4a0070bfa941118e92790ed29fd252' delivered to topic 'test_topic', partition #1, offset #2
DEBUG 09:35:03.797 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.829 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.829 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('9f6437925e5a4ba88c2b5401b879f4f2','9f6437925e5a4ba88c2b5401b879f4f2',1677749703797,0.507293704117725);
DEBUG 09:35:03.829 - Message key '9f6437925e5a4ba88c2b5401b879f4f2' delivered to topic 'test_topic', partition #4, offset #4
DEBUG 09:35:03.831 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.860 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.861 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('202d3f13acfa4a688777a2f0551abc8b','202d3f13acfa4a688777a2f0551abc8b',1677749703830,0.6967479964706729);
DEBUG 09:35:03.861 - Message key '202d3f13acfa4a688777a2f0551abc8b' delivered to topic 'test_topic', partition #2, offset #1
DEBUG 09:35:03.861 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.890 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.890 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('3414a040925f4097bd5ff24311bc8e3d','3414a040925f4097bd5ff24311bc8e3d',1677749703861,0.3011558402586926);
DEBUG 09:35:03.890 - Message key '3414a040925f4097bd5ff24311bc8e3d' delivered to topic 'test_topic', partition #1, offset #3
DEBUG 09:35:03.891 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.916 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.916 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('912e5a52a59b456d95eb35802a6110af','912e5a52a59b456d95eb35802a6110af',1677749703890,0.12099543074077346);
DEBUG 09:35:03.916 - Message key '912e5a52a59b456d95eb35802a6110af' delivered to topic 'test_topic', partition #4, offset #5
DEBUG 09:35:03.917 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.944 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.944 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('60fa8a37782e47f0b52d47929d1c3743','60fa8a37782e47f0b52d47929d1c3743',1677749703916,0.7574802889004556);
DEBUG 09:35:03.944 - Message key '60fa8a37782e47f0b52d47929d1c3743' delivered to topic 'test_topic', partition #3, offset #2
DEBUG 09:35:03.945 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.969 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.969 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('4746848f382d4b81ba97168186529022','4746848f382d4b81ba97168186529022',1677749703944,0.7432958384878651);
DEBUG 09:35:03.969 - Message key '4746848f382d4b81ba97168186529022' delivered to topic 'test_topic', partition #3, offset #3
DEBUG 09:35:03.970 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:03.996 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:03.996 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('e07ac84477fd42428f5a635e6c5dcc9b','e07ac84477fd42428f5a635e6c5dcc9b',1677749703969,0.9093017644064006);
DEBUG 09:35:03.996 - Message key 'e07ac84477fd42428f5a635e6c5dcc9b' delivered to topic 'test_topic', partition #5, offset #0
DEBUG 09:35:03.997 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.030 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.031 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('fd39be8d962d4970be54734416cb6bdc','fd39be8d962d4970be54734416cb6bdc',1677749703996,0.001851234979534766);
DEBUG 09:35:04.031 - Message key 'fd39be8d962d4970be54734416cb6bdc' delivered to topic 'test_topic', partition #3, offset #4
DEBUG 09:35:04.032 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.059 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.059 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('f2d4666861aa48e685f07d01f6fca4d9','f2d4666861aa48e685f07d01f6fca4d9',1677749704031,0.11347558190229734);
DEBUG 09:35:04.059 - Message key 'f2d4666861aa48e685f07d01f6fca4d9' delivered to topic 'test_topic', partition #5, offset #1
DEBUG 09:35:04.060 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.087 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.087 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('036017f566774155b3469123600fd1f5','036017f566774155b3469123600fd1f5',1677749704060,0.14796327150898247);
DEBUG 09:35:04.087 - Message key '036017f566774155b3469123600fd1f5' delivered to topic 'test_topic', partition #5, offset #2
DEBUG 09:35:04.088 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.115 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.115 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('7a036b11914a40ad90878d8768b04055','7a036b11914a40ad90878d8768b04055',1677749704087,0.476991507183701);
DEBUG 09:35:04.115 - Message key '7a036b11914a40ad90878d8768b04055' delivered to topic 'test_topic', partition #4, offset #6
DEBUG 09:35:04.116 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.160 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.160 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b6cd2f7efe2d42c3b0b36e9b6d1ecdd3','b6cd2f7efe2d42c3b0b36e9b6d1ecdd3',1677749704115,0.745567630430962);
DEBUG 09:35:04.160 - Message key 'b6cd2f7efe2d42c3b0b36e9b6d1ecdd3' delivered to topic 'test_topic', partition #2, offset #2
DEBUG 09:35:04.161 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.187 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.187 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('59d3d8ea997d4124b8170b4a85390a69','59d3d8ea997d4124b8170b4a85390a69',1677749704160,0.1314211195256274);
DEBUG 09:35:04.187 - Message key '59d3d8ea997d4124b8170b4a85390a69' delivered to topic 'test_topic', partition #5, offset #3
DEBUG 09:35:04.188 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:35:04.213 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:35:04.213 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0d77397fa43d4fce8f3ad27767d30e66','0d77397fa43d4fce8f3ad27767d30e66',1677749704187,0.21702802002865318);
DEBUG 09:35:04.213 - Message key '0d77397fa43d4fce8f3ad27767d30e66' delivered to topic 'test_topic', partition #3, offset #5

INFO 09:35:04.213 - Comparing partitions between producer and ksqlDB stream...
INFO 09:35:09.408 - Matched partitions: 100.00%
```
- Running python script (using crc32 partitioner): `python3 producer.py --messages 25 --random_keys --debug --crc32`
```
INFO 09:36:39.206 - Validating access to ksqlDB: http://localhost:8088...
DEBUG 09:36:39.210 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.218 - http://localhost:8088 "GET / HTTP/1.1" 307 0
DEBUG 09:36:39.222 - http://localhost:8088 "GET /info HTTP/1.1" 200 132

INFO 09:36:39.236 - Creating topic: test_topic...

INFO 09:36:39.247 - Creating ksqlDB Stream: test_topic_ksql...
DEBUG 09:36:39.248 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.278 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 351
DEBUG 09:36:39.279 - ksqlDB (200): CREATE STREAM IF NOT EXISTS test_topic_ksql (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='test_topic_ksql', VALUE_FORMAT='JSON', PARTITIONS=6, REPLICAS=1);

INFO 09:36:39.280 - Producing messages to topics: test_topic and test_topic_ksql...
DEBUG 09:36:39.281 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.307 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.307 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('41375563628f4ff298e9b7b680f8350b','41375563628f4ff298e9b7b680f8350b',1677749799280,0.7217612066062618);
DEBUG 09:36:39.307 - Message key '41375563628f4ff298e9b7b680f8350b' delivered to topic 'test_topic', partition #4, offset #7
DEBUG 09:36:39.308 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.333 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.333 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c3db1e653d744a498ba8e201ea5c807e','c3db1e653d744a498ba8e201ea5c807e',1677749799307,0.7801794552836531);
DEBUG 09:36:39.333 - Message key 'c3db1e653d744a498ba8e201ea5c807e' delivered to topic 'test_topic', partition #5, offset #4
DEBUG 09:36:39.334 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.357 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.358 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('6e91f10b438346229ea84989c2aa3b36','6e91f10b438346229ea84989c2aa3b36',1677749799333,0.49594841007368007);
DEBUG 09:36:39.358 - Message key '6e91f10b438346229ea84989c2aa3b36' delivered to topic 'test_topic', partition #0, offset #1
DEBUG 09:36:39.359 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.387 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.387 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('864b845d200f4433b71b611be09995c4','864b845d200f4433b71b611be09995c4',1677749799358,0.18680028568807439);
DEBUG 09:36:39.387 - Message key '864b845d200f4433b71b611be09995c4' delivered to topic 'test_topic', partition #4, offset #8
DEBUG 09:36:39.388 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.411 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.411 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('757d14e509d245d1b6682f82df2e6541','757d14e509d245d1b6682f82df2e6541',1677749799387,0.7581447224779339);
DEBUG 09:36:39.411 - Message key '757d14e509d245d1b6682f82df2e6541' delivered to topic 'test_topic', partition #5, offset #5
DEBUG 09:36:39.412 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.436 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.436 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('ae4e1ee300cf4887b27c33de7f836887','ae4e1ee300cf4887b27c33de7f836887',1677749799411,0.30704413956103693);
DEBUG 09:36:39.436 - Message key 'ae4e1ee300cf4887b27c33de7f836887' delivered to topic 'test_topic', partition #4, offset #9
DEBUG 09:36:39.437 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.466 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.466 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0563a54e450f4a56bd6c283bb5139fab','0563a54e450f4a56bd6c283bb5139fab',1677749799436,0.558273731456149);
DEBUG 09:36:39.466 - Message key '0563a54e450f4a56bd6c283bb5139fab' delivered to topic 'test_topic', partition #3, offset #6
DEBUG 09:36:39.467 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.491 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.492 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c5fc381056bd40158ea6209b9e825f3a','c5fc381056bd40158ea6209b9e825f3a',1677749799466,0.18186861082136885);
DEBUG 09:36:39.492 - Message key 'c5fc381056bd40158ea6209b9e825f3a' delivered to topic 'test_topic', partition #2, offset #3
DEBUG 09:36:39.493 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.520 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.520 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('f7bf74b109194eb89b69b55034adbe76','f7bf74b109194eb89b69b55034adbe76',1677749799492,0.07583529317565707);
DEBUG 09:36:39.520 - Message key 'f7bf74b109194eb89b69b55034adbe76' delivered to topic 'test_topic', partition #0, offset #2
DEBUG 09:36:39.521 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.545 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.545 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('cbf1cc3a80434221b6f59f882bccf9d7','cbf1cc3a80434221b6f59f882bccf9d7',1677749799521,0.05798826219737396);
DEBUG 09:36:39.545 - Message key 'cbf1cc3a80434221b6f59f882bccf9d7' delivered to topic 'test_topic', partition #5, offset #6
DEBUG 09:36:39.546 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.571 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.572 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('e4a998167ba0446d8d4e79b3d62ff9c6','e4a998167ba0446d8d4e79b3d62ff9c6',1677749799545,0.0777392293107485);
DEBUG 09:36:39.572 - Message key 'e4a998167ba0446d8d4e79b3d62ff9c6' delivered to topic 'test_topic', partition #4, offset #10
DEBUG 09:36:39.573 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.599 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.599 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('7f1c6b65538349a888e4276933f340ef','7f1c6b65538349a888e4276933f340ef',1677749799572,0.8127143811342272);
DEBUG 09:36:39.599 - Message key '7f1c6b65538349a888e4276933f340ef' delivered to topic 'test_topic', partition #1, offset #4
DEBUG 09:36:39.600 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.626 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.626 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('6b04ae0451e04e268dbb197b39f6d642','6b04ae0451e04e268dbb197b39f6d642',1677749799599,0.26449020046469296);
DEBUG 09:36:39.626 - Message key '6b04ae0451e04e268dbb197b39f6d642' delivered to topic 'test_topic', partition #4, offset #11
DEBUG 09:36:39.627 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.653 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.653 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('021b94a50ddd40b7b5b8c0204333fe12','021b94a50ddd40b7b5b8c0204333fe12',1677749799626,0.059784726209630934);
DEBUG 09:36:39.653 - Message key '021b94a50ddd40b7b5b8c0204333fe12' delivered to topic 'test_topic', partition #0, offset #3
DEBUG 09:36:39.654 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.676 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.677 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1a6235fc25754c4b9ee001f2b9350975','1a6235fc25754c4b9ee001f2b9350975',1677749799653,0.4293694536057171);
DEBUG 09:36:39.677 - Message key '1a6235fc25754c4b9ee001f2b9350975' delivered to topic 'test_topic', partition #2, offset #4
DEBUG 09:36:39.678 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.712 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.712 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('234287509a1642adb1e2e6f0646319e5','234287509a1642adb1e2e6f0646319e5',1677749799677,0.8319958592619964);
DEBUG 09:36:39.713 - Message key '234287509a1642adb1e2e6f0646319e5' delivered to topic 'test_topic', partition #0, offset #4
DEBUG 09:36:39.714 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.739 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.739 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b394c92a6f6a493d9fa2ddd4dcae6e98','b394c92a6f6a493d9fa2ddd4dcae6e98',1677749799713,0.08879792899025518);
DEBUG 09:36:39.739 - Message key 'b394c92a6f6a493d9fa2ddd4dcae6e98' delivered to topic 'test_topic', partition #2, offset #5
DEBUG 09:36:39.740 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.766 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.767 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('d7e7c1e59c214da6a29d330fd98879c0','d7e7c1e59c214da6a29d330fd98879c0',1677749799739,0.19202672078696637);
DEBUG 09:36:39.767 - Message key 'd7e7c1e59c214da6a29d330fd98879c0' delivered to topic 'test_topic', partition #1, offset #5
DEBUG 09:36:39.768 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.795 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.795 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('4c6c3ba4db714ac3bf481b0f81bd38fb','4c6c3ba4db714ac3bf481b0f81bd38fb',1677749799767,0.28908764138200294);
DEBUG 09:36:39.795 - Message key '4c6c3ba4db714ac3bf481b0f81bd38fb' delivered to topic 'test_topic', partition #1, offset #6
DEBUG 09:36:39.796 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.822 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.822 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('038131e939324fe1a61f9314ad8dd905','038131e939324fe1a61f9314ad8dd905',1677749799795,0.5754119007160479);
DEBUG 09:36:39.822 - Message key '038131e939324fe1a61f9314ad8dd905' delivered to topic 'test_topic', partition #2, offset #6
DEBUG 09:36:39.823 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.846 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.846 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0eb6dedb80b346ccb930189897847d51','0eb6dedb80b346ccb930189897847d51',1677749799822,0.9217964236502765);
DEBUG 09:36:39.846 - Message key '0eb6dedb80b346ccb930189897847d51' delivered to topic 'test_topic', partition #3, offset #7
DEBUG 09:36:39.847 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.870 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.871 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0b72dae3fca940bb92b5a680aaad83a7','0b72dae3fca940bb92b5a680aaad83a7',1677749799846,0.15806336738344617);
DEBUG 09:36:39.871 - Message key '0b72dae3fca940bb92b5a680aaad83a7' delivered to topic 'test_topic', partition #3, offset #8
DEBUG 09:36:39.872 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.897 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.897 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('81832f860bfc444b8c3de474cf0eeac0','81832f860bfc444b8c3de474cf0eeac0',1677749799871,0.5674732268248345);
DEBUG 09:36:39.897 - Message key '81832f860bfc444b8c3de474cf0eeac0' delivered to topic 'test_topic', partition #3, offset #9
DEBUG 09:36:39.898 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.921 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.921 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('320e72432df94b6a8f04cc23a5aa872d','320e72432df94b6a8f04cc23a5aa872d',1677749799897,0.987728382181024);
DEBUG 09:36:39.921 - Message key '320e72432df94b6a8f04cc23a5aa872d' delivered to topic 'test_topic', partition #0, offset #5
DEBUG 09:36:39.922 - Starting new HTTP connection (1): localhost:8088
DEBUG 09:36:39.945 - http://localhost:8088 "POST /ksql HTTP/1.1" 200 2
DEBUG 09:36:39.945 - ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('2c4811cc2ef54f2898d45ac611e8d6c7','2c4811cc2ef54f2898d45ac611e8d6c7',1677749799921,0.298493296183023);
DEBUG 09:36:39.945 - Message key '2c4811cc2ef54f2898d45ac611e8d6c7' delivered to topic 'test_topic', partition #5, offset #7

INFO 09:36:39.945 - Comparing partitions between producer and ksqlDB stream...
INFO 09:36:45.009 - Matched partitions: 20.00%
INFO 09:36:45.010 - Key exceptions
 - Key '6e91f10b438346229ea84989c2aa3b36': 'test_topic' = 0 | 'test_topic_ksql' = 4
 - Key 'f7bf74b109194eb89b69b55034adbe76': 'test_topic' = 0 | 'test_topic_ksql' = 2
 - Key '021b94a50ddd40b7b5b8c0204333fe12': 'test_topic' = 0 | 'test_topic_ksql' = 4
 - Key '234287509a1642adb1e2e6f0646319e5': 'test_topic' = 0 | 'test_topic_ksql' = 4
 - Key '320e72432df94b6a8f04cc23a5aa872d': 'test_topic' = 0 | 'test_topic_ksql' = 5
 - Key '7f1c6b65538349a888e4276933f340ef': 'test_topic' = 1 | 'test_topic_ksql' = 5
 - Key 'd7e7c1e59c214da6a29d330fd98879c0': 'test_topic' = 1 | 'test_topic_ksql' = 0
 - Key '4c6c3ba4db714ac3bf481b0f81bd38fb': 'test_topic' = 1 | 'test_topic_ksql' = 2
 - Key 'c5fc381056bd40158ea6209b9e825f3a': 'test_topic' = 2 | 'test_topic_ksql' = 3
 - Key '038131e939324fe1a61f9314ad8dd905': 'test_topic' = 2 | 'test_topic_ksql' = 0
 - Key '0563a54e450f4a56bd6c283bb5139fab': 'test_topic' = 3 | 'test_topic_ksql' = 1
 - Key '0eb6dedb80b346ccb930189897847d51': 'test_topic' = 3 | 'test_topic_ksql' = 0
 - Key '0b72dae3fca940bb92b5a680aaad83a7': 'test_topic' = 3 | 'test_topic_ksql' = 4
 - Key '81832f860bfc444b8c3de474cf0eeac0': 'test_topic' = 3 | 'test_topic_ksql' = 0
 - Key '41375563628f4ff298e9b7b680f8350b': 'test_topic' = 4 | 'test_topic_ksql' = 2
 - Key '864b845d200f4433b71b611be09995c4': 'test_topic' = 4 | 'test_topic_ksql' = 1
 - Key 'ae4e1ee300cf4887b27c33de7f836887': 'test_topic' = 4 | 'test_topic_ksql' = 2
 - Key 'e4a998167ba0446d8d4e79b3d62ff9c6': 'test_topic' = 4 | 'test_topic_ksql' = 1
 - Key 'c3db1e653d744a498ba8e201ea5c807e': 'test_topic' = 5 | 'test_topic_ksql' = 1
 - Key '2c4811cc2ef54f2898d45ac611e8d6c7': 'test_topic' = 5 | 'test_topic_ksql' = 4
```
- Once done with it, stop your docker containers: `docker-compose down`
