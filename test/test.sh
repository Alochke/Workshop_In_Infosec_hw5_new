#!/bin/bash

for n in {1..10}
do
    echo "testing fasle$n"
    curl --upload-file fasle$n server
    sleep 5
    curl "server/idk?name=$(cat "false$n")"
    sleep 5
done

for n in {1..10}
do
    echo "testing true$n"
    curl --upload-file true$n server
    sleep 5
    curl "server/idk?name=$(cat "true$n")"
    sleep 5
done