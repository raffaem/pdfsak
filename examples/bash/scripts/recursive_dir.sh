#!/usr/bin/env bash

# This example loops over the PDFs in a directory and run the same command on each of them

if [ -d "../../output/recursive_dir" ];
then
    rm -rf ../../output/recursive_dir
fi

mkdir ../../output/recursive_dir
cp ../../input/article1.pdf ../../output/recursive_dir
cp ../../input/article2.pdf ../../output/recursive_dir
cp ../../input/presentation.pdf ../../output/recursive_dir

../../../pdfsak --recursive-dir ../../output/recursive_dir --replace-input --nup 2 2
