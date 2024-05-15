#!/bin/bash

for file in *
do
    echo "testin $(file)"
    curl --upload-file $file server
    sleep 5
    curl "server/idk?name=$(cat file)"
    sleep 5
done