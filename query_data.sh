#!/usr/bin/env bash

function query_data(){
# change the query parameters as you wish
query_json='{
  "main_table": "vessel",
  "where": "dynamic_vessel.lat > %s",
  "params": [0.0],
  "order_by": "timestamp DESC",
  "limit": 10
}'

URL="http://localhost:5000/query_data"

# Loop through each JSON object using jq
curl -k -X GET "$URL" \
  -H "Content-Type: application/json" \
  -d "$query_json"

}
query_data
