# -*- encoding: utf-8 -*-
#
#

from threading import *
from Queue import Queue as _Queue, Empty
from . import fetch

# regular fetch
def feed_fetch(pool, ctlr_list, db = None):
  import importlib
  from . import DB

  if db is None: _db = DB()
  else: _db = db

  for pkg in ctlr_list:
    module = importlib.import_module('lib.%s' % pkg)
    for ctlr in module.Ctlrs:
      ctlr().feed(pool, _db)

  if db is None: _db.disconnect()

# Revisits
def feed_revisit(pool, db = None):
  from . import DB

  if db is None: _db = DB()
  else: _db = db

  if db is None: _db.disconnect()

# catchup
def feed_catchup(pool, db = None):
  from . import DB

  if db is None: _db = DB()
  else: _db = db

  if db is None: _db.disconnect()



class Queue(_Queue):
  """Job Queue, 包裝底層的 fetcher"""

  def __init__(self, maxsize = 0):
    _Queue.__init__(self, maxsize)

    self._url_cache_lock = RLock()
    self.url_cache = set()

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
    if not self.put_url(url): return False

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
  並傳入 payload, pool, db 三個參數"""
  def __init__(self, pool):
    from . import DB, say
    Thread.__init__(self)

    say('initiated', self)
    self.pool = pool
    self.db = DB()

  def run(self):
    from . import fetch
    from time import sleep

    sleep(1)

    while True:
      try: payload = self.pool.get(False, 6)
      except Empty: break

      try:
        payload = fetch(payload)
        payload['cb'](payload, db = self.db, pool = self.pool)
      except:
        import traceback
        print("\n=== Parse Error ===")
        traceback.print_exc()
      finally:
        self.pool.task_done()
