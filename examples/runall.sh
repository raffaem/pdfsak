#!/usr/bin/env bash

rm -rf ./output
mkdir ./output
cd ./scripts

for f in ./*.sh
do
    echo "Running $f"
    source $f
done
