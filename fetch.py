#!/usr/bin/python
#-*- encoding:utf-8 -*-

# ==========================


# CTLR-based Fetches
ctlr_list = [
  'appledaily',
  'chinatimes',
  'libertytimes',
]

from lib import proc, conf, Queue, DB
from threading import Condition

jobs = Queue()
db = DB()

# lib.Ctlr_Base.do_fetch(ctlr_list)
proc.feed_fetch(jobs, ctlr_list, db)

# Revisits
proc.feed_revisit(jobs, db)

db.disconnect()

# initiate worker threads
for i in xrange(conf['config']['threads']):
  proc.Worker(jobs).start()

if (jobs.unfinished_tasks > 0):
  jobs.join()
