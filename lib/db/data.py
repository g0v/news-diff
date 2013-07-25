# -*- encoding:utf-8 -*-
#
# 管理下列目標資料：
#   - fetch
#   - response
#   - article
#

from db import DB

# 不儲存的 categories
fetch_categories_ignored = ['response', 'revisit', 'rss_2_0']
# fetch_categories_ignored = []


def save_fetch(url, response, category = 'unknown', dbi = None):
  """寫入 fetches 表; 不做 unique key 檢查，僅就 category 判斷是否儲存"""

  if (category in fetch_categories_ignored): return

  sql = "INSERT INTO `fetches` (`url`, `response`, `category`) VALUES" \
    "(%(url)s, %(response)s, %(category)s)"

  DB.execute(sql, {"url": url, "response": response, "category": category}, dbi = dbi)


def save_response(payload, dbi = None):
  """ Response, 僅在 parse 失敗時寫入，因此積極重寫"""
  from json import dumps
  from datetime import datetime
  from copy import deepcopy

  from lib.util.text import md5

  # deep copy so that we don't mess up the original payload
  _payload = deepcopy(payload)
  _payload["meta"] = dumps(payload['meta'])
  _payload["response_md5"] = md5(_payload['response'])

  sql = "INSERT IGNORE INTO `responses` " + \
    "(`feed_id`, `url`, `body`, `body_hash`, `meta`) VALUES(" + \
      "(SELECT `feed_id` FROM `feeds` WHERE `url` = %(feed_url)s), " + \
      "%(url)s, %(response)s, UNHEX(%(response_md5)s), %(meta)s" + \
      ")"
  DB.execute(sql, _payload, dbi = dbi)


def save_article(payload, dbi = None):
  """更新新聞內容"""
  from json import dumps
  from datetime import datetime
  from copy import deepcopy

  from lib.util.text import md5

  # deep copy so that we don't mess up the original payload
  _payload = deepcopy(payload)
  _payload["meta"] = dumps(payload['meta'])
  _payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

  # hashtbl : html, text, meta
  _payload['html_md5'] = md5(_payload['html'])
  _payload['text_md5'] = md5(_payload['text'])
  _payload['meta_md5'] = md5(_payload['meta'])

  _save_hashtbl('article__htmls', {
    'md5': _payload['html_md5'], 'body':_payload['html']}, dbi = dbi)
  _save_hashtbl('article__texts', {
    'md5': _payload['text_md5'], 'body':_payload['text']}, dbi = dbi)
  _save_hashtbl('article__meta', {
    'md5': _payload['meta_md5'], 'body': _payload['meta']}, dbi = dbi)

  # hashtbl: url
  _payload['url_md5'] = md5(_payload['url'])
  _payload['url_read_md5'] = md5(_payload['url_read'])
  _payload['url_canonical_md5'] = md5(_payload['url_canonical'])

  _save_hashtbl('article__urls', [
    {'md5': _payload['url_md5'], 'body': _payload['url']},
    {'md5': _payload['url_read_md5'], 'body': _payload['url_read']},
    {'md5': _payload['url_canonical_md5'], 'body': _payload['url_canonical']},
  ], dbi = dbi);

  # do the insert
  sql = "INSERT INTO `articles` (" \
      "`title`, `pub_ts`, `created_on`, " \
      "`feed_id`, `ctlr_id`, " \
      "`url_hash`, `url_read_hash`, `url_canonical_hash`, " \
      "`meta_hash`, `html_hash`, `text_hash`" \
    ") VALUES(" \
      "%(title)s, %(pub_ts)s, CURRENT_TIMESTAMP, " \
      "(SELECT `feed_id` FROM `feeds` WHERE `url` = %(feed_url)s), " \
      "(SELECT `ctlr_id` FROM `ctlrs` WHERE `classname` = %(ctlr_classname)s), " \
      "UNHEX(%(url_md5)s), UNHEX(%(url_read_md5)s), UNHEX(%(url_canonical_md5)s)," \
      "UNHEX(%(meta_md5)s), UNHEX(%(html_md5)s), UNHEX(%(text_md5)s)" \
    ") ON DUPLICATE KEY UPDATE last_seen_on = CURRENT_TIMESTAMP"

  DB.execute(sql, _payload, dbi = dbi)

def _save_hashtbl(tbl_name, data, dbi = None):
  """
  將 data 存入列表，接受 body, [body...] 或 [{'body':'body'}...] 的格式
  數量可能很大，因此硬寫不快取
  """
  from MySQLdb import escape_string
  from lib.util.text import md5

  if (type(data) is str):
    _data = {'md5': md5(data), 'body': data}
  elif (type(data) is dict):
    if 'md5' not in data:
      data['md5'] = md5(data['body'])
    _data = data
  elif (type(data[0]) is str):
    _data = [{'md5': md5(x), 'body': x} for x in data]
  else:
    _data = [{'md5': x['md5'] if 'md5' in x else md5(x['body']), 'body': x['body']} for x in data]

  sql = "INSERT IGNORE INTO `%s` (`body`, `hash`) VALUES " % escape_string(tbl_name)
  sql += "(%(body)s, UNHEX(%(md5)s))"

  DB.execute(sql, _data, dbi = dbi)

