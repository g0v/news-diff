#!/usr/bin/python
#-*- encoding:utf-8 -*-

# CTLR-based Fetches
ctlr_list = [
  'appledaily',
  'chinatimes',
  'libertytimes',
]

from threading import Condition
from lib import proc, conf, Queue, Worker, DB

jobs = Queue()
db = DB()

proc.feed_fetch(jobs, ctlr_list, db)
proc.feed_revisit(jobs, db)

db.disconnect()

# initiate worker threads
for i in xrange(conf['config']['threads']):
  Worker(jobs).start()

if (jobs.unfinished_tasks > 0):
  jobs.join()

print(jobs.get_stats())
