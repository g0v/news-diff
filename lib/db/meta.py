# -*- encoding:utf-8 -*-
#
# 管理下列 metadata ：
#   - host
#   - feed: 對應至所有資料來源 (eg, RSS, web page)，在 article 中作為 FK
#   - ctlr: 對應至所有被調用過的 ctlr，在 article 中作為 FK
#   - ctlr_feed:

from db import DB

_cache_host_urls = set()
_cache_feed_urls = set()
_cache_ctlr_classnames = set()
_cache_ctlr_feed = set()

#
# Host
# 數量有限且使用數值 id，快取避免重覆寫入
#
def save_host(host, dbi = None):
  cache = _cache_host_urls
  _update_host_cache(dbi = dbi)
  if (host['url'] in cache): return

  sql = "INSERT IGNORE INTO `hosts` (`name`, `url`) " \
    "VALUES (%(name)s, %(url)s)"

  DB.execute(sql, host, dbi = dbi)
  cache.add(host['url'])

def _update_host_cache(dbi = None):
  cache = _cache_host_urls
  sql = 'SELECT `url` FROM `hosts`'
  _cache_host_urls.update([x[0] for x in DB.query(sql, dbi = dbi)])

#
# feed
# 數量有限且使用數值 id，快取避免重覆寫入
#
def save_feed(source, dbi = None):
  cache = _cache_feed_urls
  _update_feed_cache(dbi = dbi)
  if (source['url'] in cache): return

  sql = "INSERT IGNORE INTO `feeds` (`url`, `title`, `host_id`" \
    ") VALUES (%(url)s, %(title)s, " \
    "(SELECT `host_id` FROM `hosts` WHERE `url` = %(host_url)s))"

  DB.execute(sql, source, dbi = dbi)
  cache.add(source['url'])

def _update_feed_cache(dbi = None):
  cache = _cache_feed_urls
  sql = 'SELECT `url` FROM `feeds`'
  cache.update([x[0] for x in DB.query(sql, dbi = dbi)])

#
# ctlr
# 數量有限且使用數值 id，快取避免重覆寫入
#

def save_ctlr(ctlr, dbi = None):
  cache = _cache_ctlr_classnames
  _update_ctlr_cache(dbi = dbi)
  if (ctlr['classname'] in cache): return

  sql = "INSERT IGNORE INTO `ctlrs` (`classname`, `created_on`" \
    ") VALUES (%(classname)s, %(created_on)s)"

  DB.execute(sql, ctlr, dbi = dbi)
  cache.add(ctlr['classname'])

def _update_ctlr_cache(dbi = None):
  cache = _cache_ctlr_classnames
  sql = 'SELECT `classname` FROM `ctlrs`'
  cache.update([x[0] for x in DB.query(sql, dbi = dbi)])

#
# ctlr_feed
# 數量不少，但可能造成大量寫入，還是做 cache
#
def save_ctlr_feed(pair, dbi = None):
  cache = _cache_ctlr_feed
  _update_ctlr_feed_cache()
  if (pair['url'], pair['classname']) in cache: return

  sql = "INSERT IGNORE INTO `ctlr_feed` (" \
      "`feed_id`, `ctlr_id`" \
    ") VALUES ("\
      "(SELECT `feed_id` FROM `feeds` WHERE `url` = %(url)s), " \
      "(SELECT `ctlr_id` FROM `ctlrs` WHERE `classname` = %(classname)s)" \
    ")"

  DB.execute(sql, pair, dbi = dbi)
  cache.add((pair['url'], pair['classname']))

def _update_ctlr_feed_cache(dbi = None):
  cache = _cache_ctlr_feed
  sql = 'SELECT `f`.`url`, `c`.`classname` FROM ' \
  '`ctlr_feed` `cf` NATURAL JOIN `feeds` `f` NATURAL JOIN `ctlrs` `c`'
  cache.update(DB.query(sql, dbi = dbi))
