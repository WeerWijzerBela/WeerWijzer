repositories=$(doctl registry repository list -o json | jq -r '.[].name')

for repo in $repositories; do
    echo "Processing repository: $repo"

    # List and sort tags for the repository, keeping the latest 2
    tags_to_delete=$(doctl registry repository list-tags $repo -o json | jq -r '.[] | .Tag' | sort -r | tail -n +3)

    for tag in $tags_to_delete; do
        echo "Deleting tag $tag from $repo"
        # Delete the tag
        doctl registry repository delete-manifest $repo $tag --force
    done
done