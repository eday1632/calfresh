#!/bin/bash

source /srv/calfresh/venv/bin/activate

rm /var/log/calfresh.log
touch /var/log/calfresh.log

cd /srv/calfresh

git pull

python /srv/calfresh/code/app.py

git add .
git commit -am "ran the daily check. updating files."
git push

cat /var/log/calfresh.log | mail -s 'Daily Log' ericday87@gmail.com
