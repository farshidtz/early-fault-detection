#!/bin/bash

for i in `seq 1 $1`;
do
    rname="python-agent-ABU"$i
    port=$((9100+$i))
    echo "Starting agent named $rname on port $port"
    
	python -u pyroAdapter.py --bname=Agent --bpath=/agent/agent.py \
        --host=python-agent --port=$port --nathost=python-agent --natport=$port \
        --rname=$rname --ns &
done

sleep infinity