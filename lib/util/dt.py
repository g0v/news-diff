# -*- coding: utf-8 -*-
#
#
def to_date(value):
  """將 value 轉換為 datetime object, 包含時差資訊"""
  from dateutil import parser
  from datetime import datetime

  mytype = type(value)

  if mytype is int or mytype is float:
    # interpret as timestamp, utc
    return datetime(value)

  if mytype is datetime:
    return value

  dt = parser.parse(value)
  return dt

def to_timestamp(value):
  mytype = type(value)
  if mytype is int or mytype is float:
    return value

  import time
  return time.mktime(to_date(value).utctimetuple())
