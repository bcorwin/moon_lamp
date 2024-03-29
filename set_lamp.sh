#!/bin/bash

# Kill lamp procces, moonlamp, and its child
CPID=$(pgrep -P $(cat moonlamp.pid))
sudo kill -s TERM $(cat setlamp.pid)
sudo kill -s TERM $(cat moonlamp.pid)
if [ -z "$CPID" ]
then
    true
else
    sudo kill -s TERM $CPID
fi

# Make sure the process was actually killed
sleep .5
PID=$(<"moonlamp.pid")
if [ -e /proc/$PID ]
then
    echo "Process: $PID is still running"
    exit 2
fi

# Start the new prcoess
echo $$ > setlamp.pid
sudo  python3 -m src.set_lamp "$@" &>> flask.log  & echo $! > moonlamp.pid

# If above fails, set lamp to a failed pattern
if  wait $(<"moonlamp.pid")
then
    true
else
    sudo python3 -m src.set_lamp -s error_screen --delay=600 &>> flask.log & echo $! > moonlamp.pid
    exit 1
fi
