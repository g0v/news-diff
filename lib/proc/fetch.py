# -*- coding: utf-8 -*-
#
#

def feed_fetch(pool, ctlr_list, dbi = None):
  """透過 Ctlr_Base_RSS 抓取新文章"""
  import importlib
  from lib import DB

  if dbi is None: _dbi = DB()
  else: _dbi = dbi

  for pkg in ctlr_list:
    module = importlib.import_module('ctlr.%s' % pkg)
    for ctlr in module.Ctlrs:
      ctlr().feed(pool, dbi = _dbi)

  if dbi is None: _dbi.disconnect()

