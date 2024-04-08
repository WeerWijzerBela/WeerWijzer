#!/bin/bash

repositories=$(doctl registry repository list -o json | jq -r '.[].name')

for repo in $repositories; do
   echo "Processing repository: $repo"

   # List and sort tags for the repository, keeping the latest 2
   tags_to_delete=$(doctl registry repository list-tags $repo -o json | jq -r '.[] | .tag +" " + .manifest_digest' | sort -r | tail -n +3 )

   echo "$tags_to_delete" | while read line; do
       tag=$(echo "$line" | cut -d ' ' -f1)
       digest=$(echo "$line" | cut -d ' ' -f2)

       if [ ! -z "$digest" -a "$digest" != "null" ]; then
            echo "Deleting tag: $tag, Digest: $digest"
            doctl registry repository delete-manifest $repo $digest --force
        else
            echo "Invalid digest for tag $tag, skipping..."
        fi
   done
done
