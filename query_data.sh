#!/usr/bin/env bash

function query_data_1(){
# change the query parameters as you wish
query_json='{
  "main_table": "vessel",
  "where": "speedoverground > %s",
  "params": [0.5],
  "order_by": "timestamp DESC",
  "limit": 10000
}'

URL="http://localhost:5000/query_data"

# Loop through each JSON object using jq
curl -k -X GET "$URL" \
  -H "Content-Type: application/json" \
  -d "$query_json" \
  -o query_results/query_result_1.txt \
  -w "\n Status: %{http_code} -> Time Total: %{time_total}s\nDownload Speed: %{speed_download} bytes/sec -> result saved under query_results/\n"

}


function query_data_2(){
# change the query parameters as you wish
query_json='{
  "main_table": "vessel",
  "where": "timestamp >= %s AND timestamp <= %s",
  "params": ["2015-09-30 22:05:36", "2015-10-10 22:05:36"],
  "order_by": "timestamp DESC",
  "limit": 100000
}'

URL="http://localhost:5000/query_data"

curl -k -X GET "$URL" \
  -H "Content-Type: application/json" \
  -d "$query_json" \
  -o query_results/query_result_2.txt \
  -w "\n Status: %{http_code} -> Time Total: %{time_total}s\nDownload Speed: %{speed_download} bytes/sec -> result saved under query_results/\n"

}

function query_data_3(){
# change the query parameters as you wish
query_json='{
  "main_table": "vessel",
  "where": "country_code = %s ",
  "params": [228],
  "order_by": "timestamp DESC",
  "limit": 100000
}'

URL="http://localhost:5000/query_data"

curl -k -X GET "$URL" \
  -H "Content-Type: application/json" \
  -d "$query_json" \
  -o query_results/query_result_3.txt \
  -w "\n Status: %{http_code} -> Time Total: %{time_total}s\nDownload Speed: %{speed_download} bytes/sec -> result saved under query_results/\n"

}
function query_data_4(){

  query_json='{
  "main_table": "voyage",
  "where": "dynamic_voyage.shipname LIKE %s",
  "params": ["%BINDY%"],
  "limit": 10
}'

URL="http://localhost:5000/query_data"

curl -k -X GET "$URL" \
  -H "Content-Type: application/json" \
  -d "$query_json" \
  -o query_results/query_result_4.txt \
  -w "\n Status: %{http_code} -> Time Total: %{time_total}s\nDownload Speed: %{speed_download} bytes/sec -> result saved under query_results/\n"

}


echo "starting new query"
query_data_1
echo "/n"
echo "-------------------------------------"
echo "starting new query trying to find by time range"
query_data_2
echo "/n"
echo "-------------------------------------"
echo "starting new query trying to find by country code"
query_data_3
echo "/n"
echo "-------------------------------------"
echo "starting new query trying to find by shipname"
query_data_4

