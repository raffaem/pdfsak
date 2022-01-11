#!/usr/bin/env bash

# This example adds a watermark

../../../pdfsak --input-file ../../input/presentation.pdf --output ../../output/watermark.pdf --watermark ../../input/tux.png br 0.5 0.5 0.3 0.5 --overwrite
