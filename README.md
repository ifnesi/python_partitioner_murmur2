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
- Waiting until you can access C3: `http://127.0.0.1:9021/`
- Running python script (using murmur2_random partitioner): `python3 producer.py --messages 25 --random_keys --verbose`
```
Creating topic: test_topic...
Creating ksqlDB Stream: test_topic_ksql...
ksqlDB (200): CREATE STREAM IF NOT EXISTS test_topic_ksql (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='test_topic_ksql', VALUE_FORMAT='JSON', PARTITIONS=6, REPLICAS=1);
Producing messages to topics: test_topic and test_topic_ksql...
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('a745dd306a044352a695dedb537e0bab','a745dd306a044352a695dedb537e0bab',1677697189422,0.5807096780778197);
Message key 'a745dd306a044352a695dedb537e0bab' delivered to topic 'test_topic', partition #2, offset #842
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('413b5828560441f5b9d46f24b7b81fc0','413b5828560441f5b9d46f24b7b81fc0',1677697189438,0.18276128871193542);
Message key '413b5828560441f5b9d46f24b7b81fc0' delivered to topic 'test_topic', partition #1, offset #824
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('061fc665965e41c7874bf91282ea463e','061fc665965e41c7874bf91282ea463e',1677697189454,0.3465794424087022);
Message key '061fc665965e41c7874bf91282ea463e' delivered to topic 'test_topic', partition #0, offset #910
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('97bd697dff8e49f5a9120e09c95596cb','97bd697dff8e49f5a9120e09c95596cb',1677697189476,0.9584773095312257);
Message key '97bd697dff8e49f5a9120e09c95596cb' delivered to topic 'test_topic', partition #0, offset #911
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('de50a35ea0dc404fb7c3ec0baa05835b','de50a35ea0dc404fb7c3ec0baa05835b',1677697189491,0.3068885961071216);
Message key 'de50a35ea0dc404fb7c3ec0baa05835b' delivered to topic 'test_topic', partition #5, offset #875
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('81e53804c0c54aeaafc3d5e7c09106eb','81e53804c0c54aeaafc3d5e7c09106eb',1677697189506,0.7532134347858345);
Message key '81e53804c0c54aeaafc3d5e7c09106eb' delivered to topic 'test_topic', partition #5, offset #876
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1f23bc6b74b14306bb068834feb92668','1f23bc6b74b14306bb068834feb92668',1677697189523,0.6280413480839526);
Message key '1f23bc6b74b14306bb068834feb92668' delivered to topic 'test_topic', partition #2, offset #843
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('092cd52b3ca94716ae60fccfdfe5690e','092cd52b3ca94716ae60fccfdfe5690e',1677697189539,0.8756246622687729);
Message key '092cd52b3ca94716ae60fccfdfe5690e' delivered to topic 'test_topic', partition #1, offset #825
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('08958bb31c9e405c9e72f74e80b4fb2e','08958bb31c9e405c9e72f74e80b4fb2e',1677697189556,0.5942297283068747);
Message key '08958bb31c9e405c9e72f74e80b4fb2e' delivered to topic 'test_topic', partition #3, offset #967
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('6ebe4dc0d31446fabfd7dc89ac83e564','6ebe4dc0d31446fabfd7dc89ac83e564',1677697189572,0.9985387027701493);
Message key '6ebe4dc0d31446fabfd7dc89ac83e564' delivered to topic 'test_topic', partition #1, offset #826
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('17409439746b4e959ab7cb59fcf8ad8e','17409439746b4e959ab7cb59fcf8ad8e',1677697189589,0.07306521373219943);
Message key '17409439746b4e959ab7cb59fcf8ad8e' delivered to topic 'test_topic', partition #1, offset #827
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c33189672d6c4a85bacb0313f0da220c','c33189672d6c4a85bacb0313f0da220c',1677697189603,0.3980818253716435);
Message key 'c33189672d6c4a85bacb0313f0da220c' delivered to topic 'test_topic', partition #2, offset #844
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('29557c3f945c4af6974daebb37c49359','29557c3f945c4af6974daebb37c49359',1677697189619,0.0012952810548919613);
Message key '29557c3f945c4af6974daebb37c49359' delivered to topic 'test_topic', partition #5, offset #877
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('4dade117008a4f05b8f9b9337bc5045b','4dade117008a4f05b8f9b9337bc5045b',1677697189635,0.6659995411666794);
Message key '4dade117008a4f05b8f9b9337bc5045b' delivered to topic 'test_topic', partition #1, offset #828
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('89f55f88416e4ae5949bbb60b0abfa7f','89f55f88416e4ae5949bbb60b0abfa7f',1677697189651,0.30121708833388317);
Message key '89f55f88416e4ae5949bbb60b0abfa7f' delivered to topic 'test_topic', partition #1, offset #829
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('7e2bbadc2cd049a6bfd88deb6b4ded44','7e2bbadc2cd049a6bfd88deb6b4ded44',1677697189666,0.3126517697624651);
Message key '7e2bbadc2cd049a6bfd88deb6b4ded44' delivered to topic 'test_topic', partition #2, offset #845
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('86e55e153dc34a339c32d11ddf227976','86e55e153dc34a339c32d11ddf227976',1677697189681,0.05630649963737533);
Message key '86e55e153dc34a339c32d11ddf227976' delivered to topic 'test_topic', partition #3, offset #968
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('03d1f221724c4b9ebc2ee5b30be5506d','03d1f221724c4b9ebc2ee5b30be5506d',1677697189698,0.4620902449955787);
Message key '03d1f221724c4b9ebc2ee5b30be5506d' delivered to topic 'test_topic', partition #1, offset #830
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('ebafd523b90a4af4ad45a3780f1ef0b8','ebafd523b90a4af4ad45a3780f1ef0b8',1677697189714,0.8213034973477098);
Message key 'ebafd523b90a4af4ad45a3780f1ef0b8' delivered to topic 'test_topic', partition #5, offset #878
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1643ca1b02094793a019415bea3817b4','1643ca1b02094793a019415bea3817b4',1677697189735,0.6237899825752952);
Message key '1643ca1b02094793a019415bea3817b4' delivered to topic 'test_topic', partition #2, offset #846
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('7d2b7b5517f94338aed22bc79976fbf7','7d2b7b5517f94338aed22bc79976fbf7',1677697189751,0.6143921794445945);
Message key '7d2b7b5517f94338aed22bc79976fbf7' delivered to topic 'test_topic', partition #3, offset #969
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('8be6a692c29c49d893cff144f537195d','8be6a692c29c49d893cff144f537195d',1677697189767,0.31944852377226574);
Message key '8be6a692c29c49d893cff144f537195d' delivered to topic 'test_topic', partition #5, offset #879
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('1f5b999f82644a069319cbdae39ee8d7','1f5b999f82644a069319cbdae39ee8d7',1677697189782,0.39987838380829155);
Message key '1f5b999f82644a069319cbdae39ee8d7' delivered to topic 'test_topic', partition #2, offset #847
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('8d05cd722fdb4ee2a513bdb4dc2ebf99','8d05cd722fdb4ee2a513bdb4dc2ebf99',1677697189799,0.470133726938196);
Message key '8d05cd722fdb4ee2a513bdb4dc2ebf99' delivered to topic 'test_topic', partition #4, offset #902
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('e25d58c84f1f425f968f38e2b1b8302f','e25d58c84f1f425f968f38e2b1b8302f',1677697189816,0.5775627385291505);
Message key 'e25d58c84f1f425f968f38e2b1b8302f' delivered to topic 'test_topic', partition #4, offset #903
Comparing partitions between producer and ksqlDB stream...
 - Matched partitions: 100.00%
```
- Running python script (using crc32 partitioner): `python3 producer.py --messages 25 --random_keys --verbose --crc32`
```
Creating topic: test_topic...
Creating ksqlDB Stream: test_topic_ksql...
ksqlDB (200): CREATE STREAM IF NOT EXISTS test_topic_ksql (id VARCHAR KEY, key VARCHAR, timestamp BIGINT, random_value DOUBLE) WITH (kafka_topic='test_topic_ksql', VALUE_FORMAT='JSON', PARTITIONS=6, REPLICAS=1);
Producing messages to topics: test_topic and test_topic_ksql...
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('15a2c38dcc0248ec844eead4607ee528','15a2c38dcc0248ec844eead4607ee528',1677697267554,0.7634338160015894);
Message key '15a2c38dcc0248ec844eead4607ee528' delivered to topic 'test_topic', partition #0, offset #912
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('18013c2c6082460b9a8459bcade32043','18013c2c6082460b9a8459bcade32043',1677697267576,0.4819544613731469);
Message key '18013c2c6082460b9a8459bcade32043' delivered to topic 'test_topic', partition #2, offset #848
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c2e48315d1684602a4125e5c87ad82e9','c2e48315d1684602a4125e5c87ad82e9',1677697267593,0.9495050122251408);
Message key 'c2e48315d1684602a4125e5c87ad82e9' delivered to topic 'test_topic', partition #1, offset #831
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('8723117a4eb549788694f5060c1265f2','8723117a4eb549788694f5060c1265f2',1677697267611,0.5965933797261486);
Message key '8723117a4eb549788694f5060c1265f2' delivered to topic 'test_topic', partition #0, offset #913
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('6898205bf14244b5b7418fddfd175bf1','6898205bf14244b5b7418fddfd175bf1',1677697267634,0.4506996271715962);
Message key '6898205bf14244b5b7418fddfd175bf1' delivered to topic 'test_topic', partition #0, offset #914
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0dc7294785cf454aa3f994703af07503','0dc7294785cf454aa3f994703af07503',1677697267656,0.35994769379028124);
Message key '0dc7294785cf454aa3f994703af07503' delivered to topic 'test_topic', partition #1, offset #832
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0e6e72b89c424bfbb079abeb065b40b8','0e6e72b89c424bfbb079abeb065b40b8',1677697267675,0.6490592394796523);
Message key '0e6e72b89c424bfbb079abeb065b40b8' delivered to topic 'test_topic', partition #0, offset #915
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('34e4284b11d04c42a8846461dfbbf0b5','34e4284b11d04c42a8846461dfbbf0b5',1677697267695,0.12987009902484792);
Message key '34e4284b11d04c42a8846461dfbbf0b5' delivered to topic 'test_topic', partition #2, offset #849
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('6d09417c4ea84c1a87c97f69fbc6ded5','6d09417c4ea84c1a87c97f69fbc6ded5',1677697267731,0.4024055326341094);
Message key '6d09417c4ea84c1a87c97f69fbc6ded5' delivered to topic 'test_topic', partition #1, offset #833
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('87876f8432864d17ace8d6ac6d77af14','87876f8432864d17ace8d6ac6d77af14',1677697267750,0.041021292819102606);
Message key '87876f8432864d17ace8d6ac6d77af14' delivered to topic 'test_topic', partition #1, offset #834
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('a5c000dff621406f8db67142bb950572','a5c000dff621406f8db67142bb950572',1677697267769,0.311318601764797);
Message key 'a5c000dff621406f8db67142bb950572' delivered to topic 'test_topic', partition #1, offset #835
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('df32d3e65f4142e9b569791f5c6940c7','df32d3e65f4142e9b569791f5c6940c7',1677697267788,0.7497214265156797);
Message key 'df32d3e65f4142e9b569791f5c6940c7' delivered to topic 'test_topic', partition #5, offset #880
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('e1ef0f9abb6048d5a8dce1c36e78071e','e1ef0f9abb6048d5a8dce1c36e78071e',1677697267807,0.03521203815452001);
Message key 'e1ef0f9abb6048d5a8dce1c36e78071e' delivered to topic 'test_topic', partition #3, offset #970
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('29b6b0b299a340d7aa798962abc9a1ca','29b6b0b299a340d7aa798962abc9a1ca',1677697267824,0.45120500994464496);
Message key '29b6b0b299a340d7aa798962abc9a1ca' delivered to topic 'test_topic', partition #5, offset #881
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('f1b090a449bc482d8e8eac1d412d23c4','f1b090a449bc482d8e8eac1d412d23c4',1677697267841,0.5056743263686121);
Message key 'f1b090a449bc482d8e8eac1d412d23c4' delivered to topic 'test_topic', partition #4, offset #904
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('c3f6f269088a4528a5296be600751356','c3f6f269088a4528a5296be600751356',1677697267857,0.8847439464109669);
Message key 'c3f6f269088a4528a5296be600751356' delivered to topic 'test_topic', partition #2, offset #850
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('52ae92dc057a4b69b11e4a98db161e48','52ae92dc057a4b69b11e4a98db161e48',1677697267873,0.4103252750895987);
Message key '52ae92dc057a4b69b11e4a98db161e48' delivered to topic 'test_topic', partition #3, offset #971
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('ad1e3e6aff254b3d9c8839a6d465bdf9','ad1e3e6aff254b3d9c8839a6d465bdf9',1677697267888,0.022020545154107563);
Message key 'ad1e3e6aff254b3d9c8839a6d465bdf9' delivered to topic 'test_topic', partition #0, offset #916
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('0ca8bea1b1f54669ade16424340bc1d9','0ca8bea1b1f54669ade16424340bc1d9',1677697267905,0.22668923881776049);
Message key '0ca8bea1b1f54669ade16424340bc1d9' delivered to topic 'test_topic', partition #2, offset #851
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('91d800a8a5c44a6cbf7ff5eaf71eaa9b','91d800a8a5c44a6cbf7ff5eaf71eaa9b',1677697267921,0.0683263769564687);
Message key '91d800a8a5c44a6cbf7ff5eaf71eaa9b' delivered to topic 'test_topic', partition #5, offset #882
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('5d05d06852924a688da0085e58ff9bea','5d05d06852924a688da0085e58ff9bea',1677697267937,0.37489236890800504);
Message key '5d05d06852924a688da0085e58ff9bea' delivered to topic 'test_topic', partition #1, offset #836
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('b90732155228478c9123d020086be49f','b90732155228478c9123d020086be49f',1677697267955,0.7834996298409991);
Message key 'b90732155228478c9123d020086be49f' delivered to topic 'test_topic', partition #3, offset #972
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('131727d02ef742a99b883b3d1afbfe15','131727d02ef742a99b883b3d1afbfe15',1677697267970,0.9890766438394927);
Message key '131727d02ef742a99b883b3d1afbfe15' delivered to topic 'test_topic', partition #4, offset #905
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('90936dc479c7470b9644e4c200c881c7','90936dc479c7470b9644e4c200c881c7',1677697267986,0.43688400090400115);
Message key '90936dc479c7470b9644e4c200c881c7' delivered to topic 'test_topic', partition #3, offset #973
ksqlDB (200): INSERT INTO test_topic_ksql (id,key,timestamp,random_value) VALUES ('8558e79ab2c34d86b2c3b00fcf360af9','8558e79ab2c34d86b2c3b00fcf360af9',1677697268009,0.38698926369560405);
Message key '8558e79ab2c34d86b2c3b00fcf360af9' delivered to topic 'test_topic', partition #0, offset #917
Comparing partitions between producer and ksqlDB stream...
 - Matched partitions: 12.00%
 - Key 15a2c38dcc0248ec844eead4607ee528 on topic 'test_topic' is 0, whereas on 'test_topic_ksql' is 1
 - Key 8723117a4eb549788694f5060c1265f2 on topic 'test_topic' is 0, whereas on 'test_topic_ksql' is 2
 - Key 6898205bf14244b5b7418fddfd175bf1 on topic 'test_topic' is 0, whereas on 'test_topic_ksql' is 3
 - Key 0e6e72b89c424bfbb079abeb065b40b8 on topic 'test_topic' is 0, whereas on 'test_topic_ksql' is 3
 - Key ad1e3e6aff254b3d9c8839a6d465bdf9 on topic 'test_topic' is 0, whereas on 'test_topic_ksql' is 3
 - Key c2e48315d1684602a4125e5c87ad82e9 on topic 'test_topic' is 1, whereas on 'test_topic_ksql' is 5
 - Key 0dc7294785cf454aa3f994703af07503 on topic 'test_topic' is 1, whereas on 'test_topic_ksql' is 0
 - Key 6d09417c4ea84c1a87c97f69fbc6ded5 on topic 'test_topic' is 1, whereas on 'test_topic_ksql' is 4
 - Key a5c000dff621406f8db67142bb950572 on topic 'test_topic' is 1, whereas on 'test_topic_ksql' is 2
 - Key 5d05d06852924a688da0085e58ff9bea on topic 'test_topic' is 1, whereas on 'test_topic_ksql' is 4
 - Key 18013c2c6082460b9a8459bcade32043 on topic 'test_topic' is 2, whereas on 'test_topic_ksql' is 3
 - Key 34e4284b11d04c42a8846461dfbbf0b5 on topic 'test_topic' is 2, whereas on 'test_topic_ksql' is 4
 - Key c3f6f269088a4528a5296be600751356 on topic 'test_topic' is 2, whereas on 'test_topic_ksql' is 5
 - Key 0ca8bea1b1f54669ade16424340bc1d9 on topic 'test_topic' is 2, whereas on 'test_topic_ksql' is 3
 - Key e1ef0f9abb6048d5a8dce1c36e78071e on topic 'test_topic' is 3, whereas on 'test_topic_ksql' is 2
 - Key 52ae92dc057a4b69b11e4a98db161e48 on topic 'test_topic' is 3, whereas on 'test_topic_ksql' is 2
 - Key b90732155228478c9123d020086be49f on topic 'test_topic' is 3, whereas on 'test_topic_ksql' is 5
 - Key f1b090a449bc482d8e8eac1d412d23c4 on topic 'test_topic' is 4, whereas on 'test_topic_ksql' is 3
 - Key 131727d02ef742a99b883b3d1afbfe15 on topic 'test_topic' is 4, whereas on 'test_topic_ksql' is 2
 - Key df32d3e65f4142e9b569791f5c6940c7 on topic 'test_topic' is 5, whereas on 'test_topic_ksql' is 0
 - Key 29b6b0b299a340d7aa798962abc9a1ca on topic 'test_topic' is 5, whereas on 'test_topic_ksql' is 0
 - Key 91d800a8a5c44a6cbf7ff5eaf71eaa9b on topic 'test_topic' is 5, whereas on 'test_topic_ksql' is 4
```
- Once done with it, stop your docker containers: `docker-compose down`
