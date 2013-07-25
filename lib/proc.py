# -*- encoding: utf-8 -*-
#
#

def feed_fetch(pool, ctlr_list, db = None):
  """透過 Ctlr_Base_RSS 抓取新文章"""
  import importlib
  from lib import DB

  if db is None: _db = DB()
  else: _db = db

  for pkg in ctlr_list:
    module = importlib.import_module('lib.%s' % pkg)
    for ctlr in module.Ctlrs:
      ctlr().feed(pool, _db)

  if db is None: _db.disconnect()

# Revisits
def feed_revisit(pool, db = None):
  from lib import DB

  if db is None: _db = DB()
  else: _db = db

  if db is None: _db.disconnect()

# catchup
def feed_catchup(pool, db = None):
  from lib import DB

  if db is None: _db = DB()
  else: _db = db

  if db is None: _db.disconnect()

