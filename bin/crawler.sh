#!/bin/bash

export PYTHONPATH="./"
export PATH="$PATH:/usr/local/bin:/usr/local/sbin:/usr/bin"
export ENVIRONMENT="PRODUCTION"
export BROWSER="HEADLESS_CHROME"
export ENGINEPATH="/home/pi/workspace/engine"
export LOGPATH="/home/pi/log"

ps -aux | grep "[p]ython" | grep "[c]rawler" > /dev/null 2>&1
if [[ "$?" != "0" ]]; then
	cd $ENGINEPATH
	/usr/bin/git checkout master
	/usr/bin/git pull
	/usr/bin/pip3 install -r $ENGINEPATH/requirements.txt
	if [ `ls -lad "$LOGPATH/gudanews_crawler.log" | awk '{print $5}'` -gt 10000000 ]; then mv "$LOGPATH/gudanews_crawler.log" "$LOGPATH/gudanews_crawler_`date '+%Y-%m-%d_%H-%M'`.log"; fi
	killall chromedriver > /dev/null 2>&1
	killall chromium > /dev/null 2>&1
	killall chromium-browser-v7 > /dev/null 2>&1
	killall /usr/lib/chromium/chromium > /dev/null 2>&1
	killall /usr/lib/chromium-browser/chromium-browser-v7 > /dev/null 2>&1
	/usr/bin/python3 $ENGINEPATH/crawler >> $LOGPATH/gudanews_crawler.log 2>&1
	killall chromedriver > /dev/null 2>&1
	killall chromium > /dev/null 2>&1
	killall chromium-browser-v7 > /dev/null 2>&1
	killall /usr/lib/chromium/chromium > /dev/null 2>&1
	killall /usr/lib/chromium-browser/chromium-browser-v7 > /dev/null 2>&1
fi
