# -*- encoding:utf-8 -*-
#
# 提供各類列表功能
#

def get_fresh_urls(urls, dbi = None):
  """篩選出 urls 中未曾成功抓取過者並回傳"""

  from lib import DB
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

def list_revisits(dbi = None):
  """輸出需要 revisit 的新聞列表, 包含 meta 欄位

  @see: Ctlr_Base.do_revisit()"""
  from lib import conf, Ctlr_Base

  sql = "SELECT " \
    "`a`.`created_on`, `a`.`last_seen_on`, `a`.`pub_ts`, `f`.`url`, `a`.`url`, `a`.`title`, `a`.`meta`, ( "\
    "  SELECT `c`.`classname` FROM `ctlrs` c NATURAL JOIN `ctlr_feed` `cf` " \
    "  WHERE `cf`.`feed_id` = `a`.`feed_id` ORDER BY `c`.`created_on` DESC LIMIT 1 " \
    ") `classname` " \
    "FROM `articles` a LEFT JOIN `feeds` f on f.`feed_id` = a.`feed_id` " \
    'WHERE `created_on` > CURRENT_TIMESTAMP - INTERVAL %d MINUTE' % \
    Ctlr_Base.revisit_max_min()

  return [x for x in self._load_into_list(sql) \
    if Ctlr_Base.need_revisit(x[0], x[1])]

