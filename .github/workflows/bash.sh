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

#!/bin/bash

repositories=$(doctl registry repository list -o json | jq -r '.[].name')

for repo in $repositories; do
    echo "Processing repository: $repo"

    # List and sort tags for the repository, keeping the latest 2
    tags_to_delete=$(doctl registry repository list-tags $repo -o json | jq -r '.[] | .manifest_digest' | sort -r | tail -n +3)

    echo "Digests to delete: $tags_to_delete"

    for digest in $tags_to_delete; do
        echo "Deleting manifest $digest from $repo"
        # Delete the tag using the digest
        doctl registry repository delete-manifest $repo --digest $digest --force
    done
done

