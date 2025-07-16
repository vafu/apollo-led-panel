#!/bin/bash

ADDR="192.168.50.60"
PASSWD="gallifrey"

# Automatically find all .py files in the current directory
# and loop through them for uploading.
for file in $(find . -name "*.py" -maxdepth 1); do
    echo "Uploading $file to $ADDR..."
    ~/.local/bin/webrepl_cli.py $file $ADDR:$file -p $PASSWD
done

~/.local/bin/webrepl_cli.py $ADDR -p $PASSWD

echo "All files uploaded successfully."
