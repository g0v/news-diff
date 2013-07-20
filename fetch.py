#!/usr/bin/python
#-*- encoding:utf-8 -*-

# ==========================


# RSS-based Fetches
ctlr_list = [
  'appledaily',
  #'chinatimes',
  #'libertytimes',
]

import Queue
from lib import proc, conf
from threading import Condition

# 在所有 thread 間共享的資料
tshared = {
  # 讀寫此物件所需之 lock
  'lock': Condition(),
  # 最近抓過的 (raw) url，若 feed 提供值重複則不抓
  'recent_urls' :[],
  # 本次執行抓取成功的 (raw) url，若新任務與之重複則不執行
  'scheduled_urls': []
}

pool = Queue.Queue(0)

# lib.Ctlr_Base.do_fetch(ctlr_list)
proc.feed_ctlr_list(pool, ctlr_list)

# Revisits
proc.feed_revisit(pool)

# initiate worker threads
for i in xrange(conf['fetcher']['threads']):
  proc.Worker(pool, tshared).start()

pool.join()