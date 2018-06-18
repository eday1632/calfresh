#!/usr/bin/python

from worker import Worker

worker = Worker('tbl_dfa256')

procd_tables = worker.work()
