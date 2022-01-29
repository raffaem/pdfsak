#!/usr/bin/env bash

# This example removes file-level metadata from a PDF file

exiftool -All -a ../../input/with_metadata.pdf > ../../output/remove_metadata_before.txt

../../../pdfsak --input-file ../../input/with_metadata.pdf --output ../../output/remove_metadata.pdf

exiftool -All -a ../../output/remove_metadata.pdf > ../../output/remove_metadata_after.txt

diff -u ../../output/remove_metadata_before.txt ../../output/remove_metadata_after.txt > ../../output/remove_metadata_diff.txt
