#!/bin/bash

trap ctrl_c INT


function ctrl_c() {
	kill $pid
	exit 0
}

for (( ; ; ))
do
	java -jar iot.learning.rest.agent-1.4.0-SNAPSHOT.jar &
	pid=$!
	sleep 30s
	curl --data '@statement.json' -H "Content-Type:application/json" -w "\n" http://localhost:8319/statement/add
	sleep 24h
	kill $pid
	sleep 10s
done

