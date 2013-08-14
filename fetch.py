#!/usr/bin/python
#-*- coding:utf-8 -*-

# CTLR-based Fetches
ctlr_list = [
  'appledaily',
  'chinatimes',
  'cna',
  'coolloud',
  'e_info_org_tw',
  'libertytimes',
  'newtalk',
  'udn',
]

from threading import Condition
import lib

jobs = lib.Queue()
dbi = lib.DB()

lib.proc.cleanup(dbi)

lib.proc.feed_fetch(jobs, ctlr_list, dbi)
lib.proc.feed_revisit(jobs, dbi)

dbi.disconnect()

# initiate worker threads
for i in xrange(lib.conf['config']['threads']):
  lib.Worker(jobs).start()

if (jobs.unfinished_tasks > 0):
  jobs.join()

print(jobs.get_stats())
