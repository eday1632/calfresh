#!/bin/bash

source /etc/calfresh/venv/bin/activate

cd /etc/calfresh

git pull

python /etc/calfresh/code/web_crawler.py

git add .

git commit -m "ran the daily check. adding recent pages"

git push
