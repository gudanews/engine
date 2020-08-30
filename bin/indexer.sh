#!/bin/bash

export PYTHONPATH="./:/Library/Python/3.7/site-packages"
export PATH="$PATH:/usr/local/bin/:/usr/local/git/bin:/sw/bin/:/usr/local/bin:/usr/local/:/usr/local/sbin:/usr/local/mysql/bin"
export ENVIRONMENT="PRODUCTION"
export BROWSER="HEADLESS_CHROME"

ps -aux | grep "[p]ython" | grep "[i]ndexer" > /dev/null 2>&1
if [[ "$?" != "0" ]]; then
	cd /home/pi/workspace/gudanews
	/usr/bin/git checkout master
	/usr/bin/git pull
	/usr/bin/pip3 install -r /home/pi/workspace/gudanews/requirements.txt
	if [ `ls -lad "/home/pi/log/gudanews_indexer.log" | awk '{print $5}'` -gt 10000000 ]; then mv /home/pi/log/gudanews_indexer.log "/home/pi/log/gudanews_indexer_`date '+%Y-%m-%d_%H-%M'`.log"; fi
	killall chromedriver > /dev/null 2>&1
	killall chromium > /dev/null 2>&1
	killall chromium-browser-v7 > /dev/null 2>&1
	/usr/bin/python3 /home/pi/workspace/gudanews/indexer >> /home/pi/log/gudanews_indexer.log 2>&1
	killall chromedriver > /dev/null 2>&1
	killall chromium > /dev/null 2>&1
	killall chromium-browser-v7 > /dev/null 2>&1
fi
