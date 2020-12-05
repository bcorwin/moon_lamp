#!/bin/bash

sudo pkill -F setlamp.pid
sudo pkill -F moonlamp.pid

echo $$ > setlamp.pid
sudo python3 set_lamp.py "$@" & echo $! > moonlamp.pid

# If above fails, set lamp to a failed pattern
if  wait $(<"moonlamp.pid")
then
    true
else
    sudo python3 set_lamp.py --phase-mode=fixed --phase-number=-1 & echo $! > moonlamp.pid
fi
