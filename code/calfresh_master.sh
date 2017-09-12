#!/bin/bash

source /etc/calfresh/venv/bin/activate

cd /etc/calfresh

git pull

python /etc/calfresh/code/app.py

git add .

git commit -m "ran the daily check. updating files."

git push
