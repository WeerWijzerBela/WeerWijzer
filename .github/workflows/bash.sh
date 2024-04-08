#!/bin/bash

repositories=$(doctl registry repository list -o json | jq -r '.[].name')

for repo in $repositories; do
   echo "Processing repository: $repo"

   # List and sort tags for the repository, keeping the latest 2
   tags_to_delete=$(doctl registry repository list-tags $repo -o json | jq -r '.[] |.tag +" " + .manifest_digest ' | sort -r | tail -n +3 )

   echo "$tags_to_delete" | while read line; do
       echo "Deleting manifest $line from $repo"
       # Delete the tag
       echo tag = $($line | cut -d ' ' -f1)
       echo digest = $($line | cut -d ' ' -f2)

       if [ ! -z "$digest" -a "$digest" != "null" ]; then
            echo "Deleting tag: $tag, Digest: $digest"
            doctl registry repository delete-manifest weerwijzer-app $digest
        else
            echo "Invalid digest for tag $tag, skipping..."
        fi
   done
done

