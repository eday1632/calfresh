#!/usr/bin/python

from worker import Worker

worker = Worker('tbl_cf296')

procd_tables = worker.work()
