#!/bin/bash
space=$1
template=$2
docker exec kibana /usr/share/kibana/bin/kibana saved-objects import \
  --file /templates/$template --space $space --overwrite
