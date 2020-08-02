#!/bin/bash

mysqldump -u gudaman -pGudaN3w2 gudanews > /home/pi/backup/gudanews_`date '+%Y-%m-%d_%H-%M'`.sql
