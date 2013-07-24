
  def dispatch_catchup(self, payload):
    """處理 responses 中解析失敗的資料"""
    raise Exception('Not Implemented, yet')

  # ==============================
  # Revisit
  # ==============================

  @staticmethod
  def revisit_tbl():
    return {
        #30: 0,
        180: 60,
        1440: 360,
        10080: 2880,
        43200: 20160
      }

  @staticmethod
  def revisit_max_min():
    return max(Ctlr_Base.revisit_tbl().keys())

  @staticmethod
  def need_revisit(created_on, last_seen_on):
    from datetime import datetime
    import math

    tbl = Ctlr_Base.revisit_tbl()
    now = datetime.utcnow()
    article_age = math.floor((now - created_on).total_seconds() / 60)
    visit_age = math.ceil((now - last_seen_on).total_seconds() / 60)

    tmp = filter(lambda(x): x > article_age, tbl.keys())

    if (len(tmp) == 0):
      #expired, should be filtered by DB
      return False

    interval = tbl[min(tmp)]
    return visit_age >= interval

  @staticmethod
  def do_revisit():
    """重下載必要的新聞，仿造 Base Ctlr :: dispatch_rss_2_0 meta
    並轉由 dispatch_response 處理

    @see db.list_revisits()"""

    from . import Fetcher, db
    import json

    f = Fetcher()
    ctlr_cache = {}
    revisit_list = db.list_revisits()

    print("Revisiting %d articles" % len(revisit_list))

    for x in revisit_list:
      if (x[7] not in ctlr_cache):
        (ns, cn) = x[7].rsplit('.', 1)
        module = importlib.import_module(ns)
        ctlr_cache[x[7]] = getattr(module, cn)()

      ctlr = ctlr_cache[x[7]]
      meta = json.loads(x[6])

      meta['feed_url'] = x[3]
      meta['pub_date'] = Ctlr_Base.to_timestamp(x[2])
      meta['title'] = x[5]

      f.queue(x[4], ctlr.dispatch_response, category="revisit", meta = meta)

    f.start()

  @staticmethod
  def do_fetch(ctlr_list):
    for pkg in ctlr_list:
      module = importlib.import_module('lib.%s' % pkg)

      for ctlr in module.Ctlrs:
        ctlr().run()
