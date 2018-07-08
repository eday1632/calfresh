#!/bin/bash

source /etc/calfresh/venv/bin/activate

rm -f /etc/calfresh/logs/calfresh.log
touch /etc/calfresh/logs/calfresh.log

cd /etc/calfresh

git config credential.helper store
git pull

python setup.py sdist

python /etc/calfresh/calfresh/app.py

git add .
git commit -am "ran the daily check. updating files."
git push

cat /etc/calfresh/logs/calfresh.log | mail -s 'Daily Log' ericday87@gmail.com
