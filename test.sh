#!/usr/bin/env bash


# memory profile
mprof run ./src/app.py

mprof plot \
    --title "Memory Usage" \
    --output doc/memory_profile.png

mprof clean
