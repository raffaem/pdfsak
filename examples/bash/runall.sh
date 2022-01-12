#!/usr/bin/env bash

../../pdfsak --check-all

rm -rf ../output
mkdir ../output
cd ./scripts

for f in ./*.sh
do
    echo "Running $f"
    source $f
done
