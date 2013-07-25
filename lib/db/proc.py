# -*- encoding:utf-8 -*-
#
# 提供各類列表功能
#

from db import DB

def get_fresh_urls(urls, dbi = None):
  """篩選出 urls 中未曾成功抓取過者並回傳"""

  from lib.util.text import md5
  from lib.util.net import normalize_url

  if (len(urls) == 0): return set()

  url_md5 = [{'url': x, 'md5': md5(normalize_url(x))} for x in urls]
  hashes = "(" + (",".join(["UNHEX('%s')" % x['md5'] for x in url_md5 ])) + ")"
  sql = "SELECT HEX(`hash`) FROM `article__urls` WHERE `hash` IN %s" % hashes

  ret = set(DB.query(sql, dbi = dbi))

  output = []
  for x in url_md5:
    if not (x['md5'].upper(),) in ret:
      output.append(x['url'])

  return output

def list_recent_fetches(interval_min, dbi = None):
  """輸出最近抓取的的新聞列表，以計算 revisit 對象

  i_created_on = 0
  i_last_seen_on = 1
  i_pub_ts = 2
  i_feed_url = 3
  i_canonical_url = 4
  i_title = 5
  i_meta = 6
  i_ctlr = 7

  @see: lib.proc.do_revisit()
  """
  from lib import conf, Ctlr_Base

  sql = "SELECT " \
    "a.`created_on`, a.`last_seen_on`, a.`pub_ts`, f.`url`, au.`body`, a.`title`, am.`body`, ( "\
    "  SELECT `c`.`classname` FROM `ctlrs` c NATURAL JOIN `ctlr_feed` `cf` " \
    "  WHERE `cf`.`feed_id` = `a`.`feed_id` ORDER BY `c`.`created_on` DESC LIMIT 1 " \
    ") `classname` " \
    "FROM `articles` a " \
    "LEFT JOIN `feeds` f on f.`feed_id` = a.`feed_id` " \
    "LEFT JOIN `article__urls` au on au.`hash` = a.`url_canonical_hash` " \
    "LEFT JOIN `article__meta` am on am.`hash` = a.`meta_hash` " \
    'WHERE `created_on` > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL %d MINUTE)' % \
    interval_min

  return DB.query(sql, dbi = dbi)

