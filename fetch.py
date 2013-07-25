#!/usr/bin/python
#-*- encoding:utf-8 -*-

# CTLR-based Fetches
ctlr_list = [
  'appledaily',
  'chinatimes',
  'coolloud',
  'e_info_org_tw',
  'libertytimes',
  'newtalk',
  'udn',
]

from threading import Condition
import lib

jobs = lib.Queue()
db = lib.DB()

lib.proc.feed_fetch(jobs, ctlr_list, db)
lib.proc.feed_revisit(jobs, db)

db.disconnect()

# initiate worker threads
for i in xrange(lib.conf['config']['threads']):
  lib.Worker(jobs).start()

if (jobs.unfinished_tasks > 0):
  jobs.join()

print(jobs.get_stats())
