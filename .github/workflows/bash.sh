#repositories=$(doctl registry repository list -o json | jq -r '.[].name')
#
#for repo in $repositories; do
#    echo "Processing repository: $repo"
#
#    # List and sort tags for the repository, keeping the latest 2
#    tags_to_delete=$(doctl registry repository list-tags $repo -o json | jq -r '.[] | .manifest_digest ' | sort -r | tail -n +3 | cut -d ' ' -f2)
#
#    echo "Tags to delete: $tags_to_delete"
#
#    for tag in $tags_to_delete; do
#        echo "Deleting manifest $tag from $repo"
#        # Delete the tag
#        doctl registry repository delete-manifest $repo $tag --force
#    done
#done
#!/bin/bash

repositories=$(doctl registry repository list -o json | jq -r '.[].name')

for repo in $repositories; do
    echo "Processing repository: $repo"

    # List tags with creation date/time
    tags_with_dates=$(doctl registry repository list-tags $repo --format "Tag,CreatedAt" --no-header)

    # Sort tags by creation date/time, oldest to newest
    sorted_tags=$(echo "$tags_with_dates" | sort -k2)

    # Keep only the latest 2 tags
    tags_to_delete=$(echo "$sorted_tags" | head -n -2 | cut -d ' ' -f1)

    echo "Tags to delete: $tags_to_delete"

    for tag in $tags_to_delete; do
        echo "Deleting manifest $tag from $repo"
        # Delete the tag
        doctl registry repository delete-manifest $repo $tag --force
    done
done
