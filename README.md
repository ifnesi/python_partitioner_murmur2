# python_partitioner_murmur2
There is no single/common/default partitioner for all Confluent and Apache Kafka resources/libs. For example all producers using librdkafka by default uses `crc32` (such as Python’s confluent_kafka), whilst JAVA ones uses `murmur2_random` (Kafka Streams, ksqlDB, Source Connectors, etc.).
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
                   [--verbose]

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
  --verbose             Display logs
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
- Running python script (using murmur2_random partitioner): `python3 producer.py --messages 25 --random_keys --verbose`
```
Creating topic: test_topic...
Creating ksqlDB Stream: test_topic_ksql...
ksqlDB (200): CREATE STREAM IF NOT EXISTS test_topic_ksql (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='test_topic_ksql', VALUE_FORMAT='JSON', PARTITIONS=6, REPLICAS=1);
Producing messages to topics: test_topic and test_topic_ksql...
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('f8b519073a55456dbdf2dc3738f4eae0','f8b519073a55456dbdf2dc3738f4eae0',1677697918735,0.4824223657962611);
Message key 'f8b519073a55456dbdf2dc3738f4eae0' delivered to topic 'test_topic', partition #0, offset #10
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('ab08a4f940b842ab8ef6b85f2e69444a','ab08a4f940b842ab8ef6b85f2e69444a',1677697918758,0.9941067481524888);
Message key 'ab08a4f940b842ab8ef6b85f2e69444a' delivered to topic 'test_topic', partition #4, offset #14
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('bed0d1ebb16d4497ad1ea1220e4a39c7','bed0d1ebb16d4497ad1ea1220e4a39c7',1677697918785,0.9639796298317254);
Message key 'bed0d1ebb16d4497ad1ea1220e4a39c7' delivered to topic 'test_topic', partition #3, offset #12
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('119e55f30cb544c2b762e2496480e071','119e55f30cb544c2b762e2496480e071',1677697918809,0.30304306560748573);
Message key '119e55f30cb544c2b762e2496480e071' delivered to topic 'test_topic', partition #3, offset #13
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c5d5ac8a57cb42599fa476f4b59c633a','c5d5ac8a57cb42599fa476f4b59c633a',1677697918835,0.5769306312721056);
Message key 'c5d5ac8a57cb42599fa476f4b59c633a' delivered to topic 'test_topic', partition #4, offset #15
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('f7593c21ce864068b595419d63cedcf9','f7593c21ce864068b595419d63cedcf9',1677697918858,0.6907408579722287);
Message key 'f7593c21ce864068b595419d63cedcf9' delivered to topic 'test_topic', partition #2, offset #15
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0696d71d7c6b4725afcbf37dfa04ac84','0696d71d7c6b4725afcbf37dfa04ac84',1677697918880,0.3316840160506148);
Message key '0696d71d7c6b4725afcbf37dfa04ac84' delivered to topic 'test_topic', partition #3, offset #14
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('49b45ee2a5384b2d952ba562630a735f','49b45ee2a5384b2d952ba562630a735f',1677697918901,0.19560081373173344);
Message key '49b45ee2a5384b2d952ba562630a735f' delivered to topic 'test_topic', partition #2, offset #16
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('2b1e5662fed74ad389f7bad50c10ed0c','2b1e5662fed74ad389f7bad50c10ed0c',1677697918926,0.21316204583720844);
Message key '2b1e5662fed74ad389f7bad50c10ed0c' delivered to topic 'test_topic', partition #3, offset #15
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b319322a3479467fb135358f0ef9778d','b319322a3479467fb135358f0ef9778d',1677697918949,0.9744410398130847);
Message key 'b319322a3479467fb135358f0ef9778d' delivered to topic 'test_topic', partition #3, offset #16
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('86cbdbc16e2f417fb75c7038d0507425','86cbdbc16e2f417fb75c7038d0507425',1677697918974,0.6026726432258764);
Message key '86cbdbc16e2f417fb75c7038d0507425' delivered to topic 'test_topic', partition #1, offset #9
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('db8c4854bc544a7480d2d9e9310575a3','db8c4854bc544a7480d2d9e9310575a3',1677697918998,0.5758058909060367);
Message key 'db8c4854bc544a7480d2d9e9310575a3' delivered to topic 'test_topic', partition #2, offset #17
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('96a72b4877f143879faa6fd3b1f20a16','96a72b4877f143879faa6fd3b1f20a16',1677697919021,0.6954771388787635);
Message key '96a72b4877f143879faa6fd3b1f20a16' delivered to topic 'test_topic', partition #2, offset #18
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('d969e5d0bcb74f159edb6408511d0d69','d969e5d0bcb74f159edb6408511d0d69',1677697919043,0.025921804402782578);
Message key 'd969e5d0bcb74f159edb6408511d0d69' delivered to topic 'test_topic', partition #0, offset #11
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('54812b41c7454ed290ed39516471ae7e','54812b41c7454ed290ed39516471ae7e',1677697919072,0.35734888781278573);
Message key '54812b41c7454ed290ed39516471ae7e' delivered to topic 'test_topic', partition #0, offset #12
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('cfac44f6e48f44ed8642a35e9766dbc2','cfac44f6e48f44ed8642a35e9766dbc2',1677697919094,0.3726261936892509);
Message key 'cfac44f6e48f44ed8642a35e9766dbc2' delivered to topic 'test_topic', partition #4, offset #16
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('bd60974a03a340ba9f8d4fecebfd7681','bd60974a03a340ba9f8d4fecebfd7681',1677697919115,0.8271593404456633);
Message key 'bd60974a03a340ba9f8d4fecebfd7681' delivered to topic 'test_topic', partition #0, offset #13
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('9d5af9a80192447ba193eda2797bbe3d','9d5af9a80192447ba193eda2797bbe3d',1677697919137,0.06801675209768698);
Message key '9d5af9a80192447ba193eda2797bbe3d' delivered to topic 'test_topic', partition #1, offset #10
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0bc8a52f1e2747c28845617f3d221e8f','0bc8a52f1e2747c28845617f3d221e8f',1677697919160,0.2560784435700838);
Message key '0bc8a52f1e2747c28845617f3d221e8f' delivered to topic 'test_topic', partition #1, offset #11
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('d3322c2bd6c1433ea8bca9d74cbddd17','d3322c2bd6c1433ea8bca9d74cbddd17',1677697919183,0.9700864849398574);
Message key 'd3322c2bd6c1433ea8bca9d74cbddd17' delivered to topic 'test_topic', partition #4, offset #17
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('76e24e94aa874effa12bfe4d5a76d419','76e24e94aa874effa12bfe4d5a76d419',1677697919207,0.21475436393718472);
Message key '76e24e94aa874effa12bfe4d5a76d419' delivered to topic 'test_topic', partition #5, offset #15
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b4bf83fe85d4408294ecc24ccf117841','b4bf83fe85d4408294ecc24ccf117841',1677697919229,0.11875513413144512);
Message key 'b4bf83fe85d4408294ecc24ccf117841' delivered to topic 'test_topic', partition #5, offset #16
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('4d91ada6cf8b4e0e9e29631b2985778b','4d91ada6cf8b4e0e9e29631b2985778b',1677697919256,0.7506172513843937);
Message key '4d91ada6cf8b4e0e9e29631b2985778b' delivered to topic 'test_topic', partition #1, offset #12
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1dcbc9eae48d4f2097ebec04f9d6f40a','1dcbc9eae48d4f2097ebec04f9d6f40a',1677697919284,0.9037342674113482);
Message key '1dcbc9eae48d4f2097ebec04f9d6f40a' delivered to topic 'test_topic', partition #5, offset #17
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('54af1917561e454085f53a285b3f6fba','54af1917561e454085f53a285b3f6fba',1677697919306,0.2852741063026979);
Message key '54af1917561e454085f53a285b3f6fba' delivered to topic 'test_topic', partition #3, offset #17
Comparing partitions between producer and ksqlDB stream...
 - Matched partitions: 100.00%
```
- Running python script (using crc32 partitioner): `python3 producer.py --messages 25 --random_keys --verbose --crc32`
```
Creating topic: test_topic...
Creating ksqlDB Stream: test_topic_ksql...
ksqlDB (200): CREATE STREAM IF NOT EXISTS test_topic_ksql (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='test_topic_ksql', VALUE_FORMAT='JSON', PARTITIONS=6, REPLICAS=1);
Producing messages to topics: test_topic and test_topic_ksql...
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('50d364745c2a412ca22ce8cd6f038a01','50d364745c2a412ca22ce8cd6f038a01',1677697870814,0.7458336112009191);
Message key '50d364745c2a412ca22ce8cd6f038a01' delivered to topic 'test_topic', partition #2, offset #8
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('3d7fda152da64a1196ee4ce94cdb63da','3d7fda152da64a1196ee4ce94cdb63da',1677697870840,0.5016045414680306);
Message key '3d7fda152da64a1196ee4ce94cdb63da' delivered to topic 'test_topic', partition #4, offset #10
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('34733ce577e54d71b6c729f73a1c2c0e','34733ce577e54d71b6c729f73a1c2c0e',1677697870868,0.0195431397785506);
Message key '34733ce577e54d71b6c729f73a1c2c0e' delivered to topic 'test_topic', partition #2, offset #9
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1a812ade7efb4b65b8cc7afbdb176e9b','1a812ade7efb4b65b8cc7afbdb176e9b',1677697870896,0.16141275997075477);
Message key '1a812ade7efb4b65b8cc7afbdb176e9b' delivered to topic 'test_topic', partition #1, offset #6
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('028c8a57f67d40268a7d18127e220cac','028c8a57f67d40268a7d18127e220cac',1677697870923,0.21845197120226256);
Message key '028c8a57f67d40268a7d18127e220cac' delivered to topic 'test_topic', partition #5, offset #11
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('29bbcfc224d54850ad23bdce17224806','29bbcfc224d54850ad23bdce17224806',1677697870948,0.35717747354354523);
Message key '29bbcfc224d54850ad23bdce17224806' delivered to topic 'test_topic', partition #2, offset #10
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('ab080dc855e74342ac42be1afa7252f4','ab080dc855e74342ac42be1afa7252f4',1677697870992,0.1687416670110924);
Message key 'ab080dc855e74342ac42be1afa7252f4' delivered to topic 'test_topic', partition #3, offset #6
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1e448c1a67944fb4816faf09c612bc47','1e448c1a67944fb4816faf09c612bc47',1677697871051,0.6466218610774422);
Message key '1e448c1a67944fb4816faf09c612bc47' delivered to topic 'test_topic', partition #3, offset #7
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('981ed48b45ae48fd8cc4955dbe4b195d','981ed48b45ae48fd8cc4955dbe4b195d',1677697871096,0.6711962000132042);
Message key '981ed48b45ae48fd8cc4955dbe4b195d' delivered to topic 'test_topic', partition #2, offset #11
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('eb32a6b1b6e643cf8b582c119b025aba','eb32a6b1b6e643cf8b582c119b025aba',1677697871143,0.11333870088981657);
Message key 'eb32a6b1b6e643cf8b582c119b025aba' delivered to topic 'test_topic', partition #4, offset #11
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b5c28f7c61fa4d44bf0585539b0606aa','b5c28f7c61fa4d44bf0585539b0606aa',1677697871173,0.8222140348829838);
Message key 'b5c28f7c61fa4d44bf0585539b0606aa' delivered to topic 'test_topic', partition #5, offset #12
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('fec4282748e5496cb4a01d0c0d6f186a','fec4282748e5496cb4a01d0c0d6f186a',1677697871201,0.9808271160536659);
Message key 'fec4282748e5496cb4a01d0c0d6f186a' delivered to topic 'test_topic', partition #4, offset #12
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('93f95043aaad4031bc4329f09f15c789','93f95043aaad4031bc4329f09f15c789',1677697871235,0.6595911538784018);
Message key '93f95043aaad4031bc4329f09f15c789' delivered to topic 'test_topic', partition #1, offset #7
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('adbf8bdc96f84ec1a79315833945e0ef','adbf8bdc96f84ec1a79315833945e0ef',1677697871264,0.30315902110947424);
Message key 'adbf8bdc96f84ec1a79315833945e0ef' delivered to topic 'test_topic', partition #2, offset #12
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c143119d31474323b1a4652602db98ed','c143119d31474323b1a4652602db98ed',1677697871290,0.47934871276206115);
Message key 'c143119d31474323b1a4652602db98ed' delivered to topic 'test_topic', partition #3, offset #8
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c76171c927e1449d956478aca0781e10','c76171c927e1449d956478aca0781e10',1677697871316,0.19646187450574903);
Message key 'c76171c927e1449d956478aca0781e10' delivered to topic 'test_topic', partition #2, offset #13
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('80e94962b73943af980e7d7f10564a57','80e94962b73943af980e7d7f10564a57',1677697871339,0.8653338772986416);
Message key '80e94962b73943af980e7d7f10564a57' delivered to topic 'test_topic', partition #5, offset #13
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c0cee25b6a04488d959fa335ead3f239','c0cee25b6a04488d959fa335ead3f239',1677697871363,0.47327806909792614);
Message key 'c0cee25b6a04488d959fa335ead3f239' delivered to topic 'test_topic', partition #3, offset #9
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('38bf4ab5c73a47df860537e42800842a','38bf4ab5c73a47df860537e42800842a',1677697871388,0.8870335958938961);
Message key '38bf4ab5c73a47df860537e42800842a' delivered to topic 'test_topic', partition #3, offset #10
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('e9b82ba073994f5e8489d04714f14168','e9b82ba073994f5e8489d04714f14168',1677697871414,0.09686154446750794);
Message key 'e9b82ba073994f5e8489d04714f14168' delivered to topic 'test_topic', partition #0, offset #9
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('45e3703481fc464ea16aee2d10f39daa','45e3703481fc464ea16aee2d10f39daa',1677697871442,0.7425173813109596);
Message key '45e3703481fc464ea16aee2d10f39daa' delivered to topic 'test_topic', partition #4, offset #13
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('044b7b7053f84d398afcf7bb742df47e','044b7b7053f84d398afcf7bb742df47e',1677697871466,0.028713138982128905);
Message key '044b7b7053f84d398afcf7bb742df47e' delivered to topic 'test_topic', partition #3, offset #11
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('bed8da0267704853bc76755da9944e7b','bed8da0267704853bc76755da9944e7b',1677697871503,0.6347120129394913);
Message key 'bed8da0267704853bc76755da9944e7b' delivered to topic 'test_topic', partition #1, offset #8
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('4b34f40335064d02a7fac97b8357a953','4b34f40335064d02a7fac97b8357a953',1677697871529,0.8637895057975871);
Message key '4b34f40335064d02a7fac97b8357a953' delivered to topic 'test_topic', partition #2, offset #14
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('5ebcc9efac2b45f78842176643d38783','5ebcc9efac2b45f78842176643d38783',1677697871552,0.15971217157878426);
Message key '5ebcc9efac2b45f78842176643d38783' delivered to topic 'test_topic', partition #5, offset #14
Comparing partitions between producer and ksqlDB stream...
 - Matched partitions: 8.00%
 - Key 'e9b82ba073994f5e8489d04714f14168': 'test_topic' = 0 | 'test_topic_ksql' = 2
 - Key '1a812ade7efb4b65b8cc7afbdb176e9b': 'test_topic' = 1 | 'test_topic_ksql' = 2
 - Key '93f95043aaad4031bc4329f09f15c789': 'test_topic' = 1 | 'test_topic_ksql' = 5
 - Key 'bed8da0267704853bc76755da9944e7b': 'test_topic' = 1 | 'test_topic_ksql' = 0
 - Key '50d364745c2a412ca22ce8cd6f038a01': 'test_topic' = 2 | 'test_topic_ksql' = 4
 - Key '34733ce577e54d71b6c729f73a1c2c0e': 'test_topic' = 2 | 'test_topic_ksql' = 1
 - Key '29bbcfc224d54850ad23bdce17224806': 'test_topic' = 2 | 'test_topic_ksql' = 4
 - Key '981ed48b45ae48fd8cc4955dbe4b195d': 'test_topic' = 2 | 'test_topic_ksql' = 4
 - Key 'adbf8bdc96f84ec1a79315833945e0ef': 'test_topic' = 2 | 'test_topic_ksql' = 0
 - Key 'c76171c927e1449d956478aca0781e10': 'test_topic' = 2 | 'test_topic_ksql' = 5
 - Key '4b34f40335064d02a7fac97b8357a953': 'test_topic' = 2 | 'test_topic_ksql' = 3
 - Key 'ab080dc855e74342ac42be1afa7252f4': 'test_topic' = 3 | 'test_topic_ksql' = 2
 - Key 'c143119d31474323b1a4652602db98ed': 'test_topic' = 3 | 'test_topic_ksql' = 1
 - Key 'c0cee25b6a04488d959fa335ead3f239': 'test_topic' = 3 | 'test_topic_ksql' = 0
 - Key '38bf4ab5c73a47df860537e42800842a': 'test_topic' = 3 | 'test_topic_ksql' = 4
 - Key '044b7b7053f84d398afcf7bb742df47e': 'test_topic' = 3 | 'test_topic_ksql' = 1
 - Key '3d7fda152da64a1196ee4ce94cdb63da': 'test_topic' = 4 | 'test_topic_ksql' = 0
 - Key 'eb32a6b1b6e643cf8b582c119b025aba': 'test_topic' = 4 | 'test_topic_ksql' = 2
 - Key 'fec4282748e5496cb4a01d0c0d6f186a': 'test_topic' = 4 | 'test_topic_ksql' = 0
 - Key '45e3703481fc464ea16aee2d10f39daa': 'test_topic' = 4 | 'test_topic_ksql' = 3
 - Key '028c8a57f67d40268a7d18127e220cac': 'test_topic' = 5 | 'test_topic_ksql' = 0
 - Key '80e94962b73943af980e7d7f10564a57': 'test_topic' = 5 | 'test_topic_ksql' = 1
 - Key '5ebcc9efac2b45f78842176643d38783': 'test_topic' = 5 | 'test_topic_ksql' = 2
```
- Once done with it, stop your docker containers: `docker-compose down`
