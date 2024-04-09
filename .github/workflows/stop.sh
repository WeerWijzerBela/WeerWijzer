#!/bin/bash

# Verkrijg een lijst van actieve garbage collection-taken met hun UUID's
active_gc_tasks=$(doctl registry garbage-collection get-active --format "UUID" --no-header)

# Controleer of er actieve taken zijn
if [ -z "$active_gc_tasks" ]; then
  echo "Er zijn geen actieve garbage collection-taken."
else
  # Itereer over elke UUID en voer de annulering uit
  while IFS= read -r task_id; do
    # Controleer of de UUID geldig is
    if [ -n "$task_id" ] && [[ "$task_id" != "<nil>" ]]; then
      echo $active_gc_tasks
      echo "Annuleren van garbage collection-taak met UUID: $task_id"
      doctl registry garbage-collection cancel "$task_id"
    else
      echo $active_gc_tasks
      echo "Ongeldige UUID: $task_id. Overslaan van annulering."
    fi
  done <<< "$active_gc_tasks"
fi