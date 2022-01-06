#!/usr/bin/env bash

read -p "Insert version number in the form A.B.C: " ver

# Change version in configuration file
sed -i -E "s/[0-9]+\.[0-9]+\.[0-9]+/$ver/g" pdfsak_version.py

echo "Echoing pdfsak_version.py"
cat pdfsak_version.py
read -p "Does it look correct (y/n)? " ans

if [ "$ans" = "y" ]; then
    echo "Answered yes. Proceeding."
elif [ "$ans" = "n" ]; then
    echo "Answered no. Exiting"
    exit
else
    echo "Unrecognized answer"
fi

# Create commit for version bump

git add -A
git commit -m "Bump version to $ver"

echo "Echoing commit for version bump"
git diff HEAD^

read -p "Does it look correct (y/n)? " ans

if [ "$ans" = "y" ]; then
    echo "Answered yes. Proceeding."
elif [ "$ans" = "n" ]; then
    echo "Answered no. Exiting"
    exit
else
    echo "Unrecognized answer"
fi

# Create annotated tag for this version
git tag -a v$ver -m "Version $ver"

echo "Echoing git tags"
git tag --list

read -p "Does it look correct (y/n)? " ans

if [ "$ans" = "y" ]; then
    echo "Answered yes. Proceeding."
elif [ "$ans" = "n" ]; then
    echo "Answered no. Exiting"
    exit
else
    echo "Unrecognized answer"
fi

# Push commit
git push

# Push tag
git push origin v$ver

# Build project
rm -rf dist/
rm -rf build/
rm -rf *.egg-info
python3 -m build

# Upload to PyPI
python3 -m twine upload dist/*

echo "Done. Remember to release on GitHub"
