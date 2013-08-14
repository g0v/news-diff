# -*- coding: utf-8 -*-
#
#

def feed_catchup(pool, dbi = None):
  from lib import DB

  if dbi is None: _dbi = DB()
  else: _dbi = dbi

  if dbi is None: _dbi.disconnect()

def dispatch_catchup(self, payload):
  """處理 responses 中解析失敗的資料"""
  raise Exception('Not Implemented, yet')
