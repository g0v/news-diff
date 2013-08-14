# -*- coding: utf-8 -*-
#
#

from threading import *
from Queue import Queue as _Queue, Empty

class Queue(_Queue):
  """Job Queue, 包裝底層的 fetcher

  stats 來源：
   - 主循環 (queue -> worker -> fetch and parse)
   - Ctrl_RSS 快取本次抓過的 url，因此可觸發 skipped
  """

  def __init__(self, maxsize = 0):
    _Queue.__init__(self, maxsize)

    self._url_cache_lock = RLock()
    self.url_cache = set()

    self._stats_lock = RLock()
    self._stats = {
      # 表示其它執行來源，標記為 @startpoint；結果會登記至 done / error
      'with_revisit': 0, # 透過 revisit 產生的 request
      'with_catchup': 0, # 透過 catchup 發動的資料流程，不送 request
      # 表示執行結果，標記為 @endpoint
      'done_feed': 0,
      'done_article': 0,
      'done_skipped': 0,
      'error_fetch': 0,
      'error_parse': 0,
      'error_unhandled': 0,
    }

  def get_stats(self):
    """"""
    from copy import deepcopy
    return deepcopy(self._stats)

  def log_stats(self, key):
    if key in self._stats:
      with self._stats_lock:
        self._stats[key] += 1
    else:
      raise Exception('Unknown key: %s' % key)

  def put_url(self, url):
    with self._url_cache_lock:
      if (url not in self.url_cache):
        self.url_cache.add(url)
        return True
    return False

  def put(self, url, cb, category = None, meta = None):
    # check param `cb`
    if (not callable(cb)): return False

    # check param `url`
    if not self.put_url(url):
      self.log_stats('done_skipped')
      return False

    # fill-in other params
    if (category is None): category = 'unknown'
    if (meta is None): meta = {}

    return _Queue.put(self,  {
      'url': url,
      'cb': cb,
      'category': category,
      'meta': meta
      })

class Worker(Thread):
  """Worker
  針對 pool 中項目依次抓取並調用 callback；
  並傳入 payload, pool, db 三個參數

  @endpoint
  """
  def __init__(self, pool):
    from lib import DB, logger
    Thread.__init__(self)

    logger.info('initiated', extra={'classname': self.__class__})

    self.pool = pool
    self.dbi = DB()

  def run(self):
    import traceback
    from time import sleep

    from net import fetch

    sleep(1)

    while True:
      try: payload = self.pool.get(False, 9)
      except Empty: break

      try:
        payload = fetch(payload, dbi = self.dbi)
      except:
        print("\n***\nFetch Error")
        traceback.print_exc()
        self.pool.log_stats('error_fetch')
        self.pool.task_done()
        continue

      try:
        payload['cb'](payload, dbi = self.dbi, pool = self.pool)
      except:
        print("\n***\nUnhandled Parse Error")
        traceback.print_exc()
        self.pool.log_stats('error_unhandled')
        self.pool.task_done()
        continue

      self.pool.task_done()
