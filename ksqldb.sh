#!/bin/sh
docker exec ksqldb-cli ksql $1 --execute "SET 'auto.offset.reset'='earliest'; SELECT * FROM $2 WHERE ts>=$3 EMIT CHANGES;" --output JSON --query-row-limit $4
