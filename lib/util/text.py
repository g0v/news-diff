# -*- coding: utf-8 -*-
#

def md5(text):
  from hashlib import md5
  if (type(text) is unicode): text = text.encode('utf-8')
  return md5(text).hexdigest()

def to_unicode(text):
  """將 text 轉為 unicode"""

  if type(text) is unicode: return text

  charset_tbl = ['utf-8', 'cp950']

  for charset in charset_tbl:
    try:
      tmp = unicode(text, charset)
      return tmp
    except: continue

  raise Exception("Unknown Encoding")


def pack_string(input):
  """去除字串中對人閱讀無用的字符"""
  import re
  output = re.sub('\r', '\n', input)
  output = re.sub('\n+', '\n', output)
  output = re.sub('\s+', ' ', output)
  return output.strip()
