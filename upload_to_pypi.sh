#!/usr/bin/env bash

rm -rf dist/
rm -rf build/
rm -rf *.egg-info

python3 -m build

python3 -m twine upload dist/*
