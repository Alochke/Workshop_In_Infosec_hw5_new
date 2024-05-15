#!/bin/bash

for n in *
do
    echo "testing $(n)"
    curl --upload-file $file server
    sleep 5
    curl "server/idk?name=$(cat $n)"
    sleep 5
done