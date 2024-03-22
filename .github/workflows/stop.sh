#!/bin/bash

active_gc_tasks=$(doctl registry garbage-collection list --format ID,Status --no-header | grep -c "Active")
if [ "$active_gc_tasks" -eq 0 ]; then
  echo "Er zijn geen actieve garbage collection-taken. "
else
  doctl registry garbage-collection cancel
fi
