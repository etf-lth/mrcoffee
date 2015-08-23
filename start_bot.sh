#!/bin/sh
cd /root
alsactl --file /root/asound.state restore
rm nohup.out /tmp/bot.*
nohup ./bot.py &
