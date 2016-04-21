#!/bin/bash

echo "generating manifest.txt"

> manifest.txt

for file in $(find . -type f ! -path "./manifest.sh" ! -path "./manifest.txt"); do
    size=$(stat -c%s "$file")
    hash=$(sha1sum "$file" | awk '{print $1}')
    echo "$hash;$size;${file:2}"
    echo "$hash;$size;${file:2}" >> manifest.txt
done

cat >> manifest.txt <<EOF
MANIFEST_CONFIG
EOF

echo "done"