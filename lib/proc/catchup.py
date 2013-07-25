# -*- encoding: utf-8 -*-
#
#

def feed_catchup(pool, db = None):
  from lib import DB

  if db is None: _db = DB()
  else: _db = db

  if db is None: _db.disconnect()

def dispatch_catchup(self, payload):
  """處理 responses 中解析失敗的資料"""
  raise Exception('Not Implemented, yet')
