#!/bin/bash

# Check if being ran from the right directory.
if [[ ! -f "screen_daemon.py" ]]; then
    echo "ERROR: Please run the script in the main directory."
    exit 1
fi

killall compton
/usr/bin/obs &
/usr/bin/google-chrome-stable --new-window https://app.pretzel.rocks/player &
./screen_daemon.py
