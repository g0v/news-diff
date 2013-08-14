# -*- coding: utf-8 -*-
#
#

#
#
#
_revisit_tbl = {
  #30: 0,
  180: 60,
  1440: 360,
  10080: 2880,
  43200: 20160
}

def feed_revisit(pool, dbi = None):
  """重下載必要的新聞，仿造 Base Ctlr :: dispatch_rss_2_0 meta
  並轉由 dispatch_response 處理

  @see db.list_revisits()
  @startpoint
  """
  import json
  import importlib

  from lib import db, DB, logger
  from lib.util.dt import to_timestamp

  if dbi is None: _dbi = DB()
  else: _dbi = dbi

  ctlr_cache = {}

  i_created_on = 0
  i_last_seen_on = 1
  i_pub_ts = 2
  i_feed_url = 3
  i_canonical_url = 4
  i_title = 5
  i_meta = 6
  i_ctlr = 7

  # logger.info("Found %d articles to revisit" % len(revisit_list))

  for x in db.list_recent_fetches(revisit_max_m(), dbi = dbi):
    if (not need_revisit(x[i_created_on], x[i_last_seen_on])):
      continue

    if (x[i_ctlr] not in ctlr_cache):
      (ns, cn) = x[i_ctlr].rsplit('.', 1)
      module = importlib.import_module(ns)
      ctlr_cache[x[i_ctlr]] = getattr(module, cn)()

    ctlr = ctlr_cache[x[i_ctlr]]
    meta = json.loads(x[i_meta])

    meta['feed_url'] = x[i_feed_url]
    meta['pub_date'] = to_timestamp(x[i_pub_ts])
    meta['title'] = x[i_title]

    logger.info('Revisiting %s', x[i_canonical_url], extra = {'classname': feed_revisit})
    pool.log_stats('with_revisit')
    pool.put("http://" + x[i_canonical_url], ctlr.dispatch_response, category="revisit", meta = meta)

  if dbi is None: _dbi.disconnect()

def revisit_max_m():
  """取得最長關注時間 (分鐘)；超出此值的新聞不會被 revisit"""
  return max(_revisit_tbl.keys())

def need_revisit(created_on, last_seen_on):
  from datetime import datetime
  import math

  now = datetime.utcnow()
  article_age = math.floor((now - created_on).total_seconds() / 60)
  visit_age = math.ceil((now - last_seen_on).total_seconds() / 60)

  tmp = filter(lambda(x): x > article_age, _revisit_tbl.keys())

  if (len(tmp) == 0):
    #expired, should be filtered by DB
    return False

  interval = _revisit_tbl[min(tmp)]
  return visit_age >= interval
