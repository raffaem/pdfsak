#!/usr/bin/env bash

# This example delete pages 4,5,10 and 11

../../pdfsak --input-file ../input/numbered.pdf --output ../output/delete_pages.pdf --overwrite --delete-pages "4,5,10,11" 
