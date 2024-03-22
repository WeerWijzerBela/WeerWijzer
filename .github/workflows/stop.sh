#!/bin/bash

active_gc_tasks=$(doctl registry garbage-collection list --format ID,Status --no-header | grep -c "Active")
if [ "$active_gc_tasks" -eq 0 ]; then
  echo "Er zijn geen actieve garbage collection-taken. "
  run_gc=true
else
  echo "Er zijn nog actieve garbage collection-taken. "
  run_gc=false
fi

if [ "$run_gc" = "false" ]; then
    doctl registry garbage-collection start --cancel-active
fi