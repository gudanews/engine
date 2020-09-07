#!/bin/bash

export PYTHONPATH="./"
export PATH="$PATH:/usr/local/bin:/usr/local/sbin:/usr/bin"
export ENVIRONMENT="PRODUCTION"
export BROWSER="HEADLESS_CHROME"
export ENGINEPATH="/home/pi/workspace/engine"
export LOGPATH="/home/pi/log"


ps -aux | grep "[p]ython" | grep "[i]ndexer" > /dev/null 2>&1
if [[ "$?" != "0" ]]; then
	cd $ENGINEPATH
	/usr/bin/git checkout master
	/usr/bin/git pull
	/usr/bin/pip3 install -r $ENGINEPATH/requirements.txt
	if [ `ls -lad "$LOGPATH/gudanews_indexer.log" | awk '{print $5}'` -gt 20000000 ]; then mv "$LOGPATH/gudanews_indexer.log" "$LOGPATH/gudanews_indexer_`date '+%Y-%m-%d_%H-%M'`.log"; fi
	killall chromedriver > /dev/null 2>&1
	killall chromium > /dev/null 2>&1
	killall chromium-browser-v7 > /dev/null 2>&1
	killall /usr/lib/chromium/chromium > /dev/null 2>&1
	killall /usr/lib/chromium-browser/chromium-browser-v7 > /dev/null 2>&1
	/usr/bin/python3 $ENGINEPATH/indexer >> $LOGPATH/gudanews_indexer.log 2>&1
	killall chromedriver > /dev/null 2>&1
	killall chromium > /dev/null 2>&1
	killall chromium-browser-v7 > /dev/null 2>&1
	killall /usr/lib/chromium/chromium > /dev/null 2>&1
	killall /usr/lib/chromium-browser/chromium-browser-v7 > /dev/null 2>&1
fi
