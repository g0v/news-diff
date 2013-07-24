# -*-encoding:utf-8 -*-
#
# 資料庫相關功能
# 每個 thread 需生成自身的 db instance；快取與一致性問題由資料庫處理
#
#

# 不儲存的 categories
fetch_categories_ignored = ['response', 'revisit', 'rss_2_0']
# fetch_categories_ignored = []

from copy import deepcopy

class DB_Base:
  """提供資料庫底層操作功能"""

  # 測試模式，禁止寫入 DB
  ignore_db_write = False

  def __init__(self, server = 'default'):
    self._conn = None
    self._server = server

  def __del__(self):
    self.disconnect()

  def disconnect(self):
    if (self._conn and self._conn.open):
      self._conn.close()

  def conn(self):
    import MySQLdb

    if (not (self._conn and self._conn.open)):
      from . import conf

      dbconf = conf['db'][self._server]

      self._conn = MySQLdb.connect(
        host=dbconf['host'],
        db=dbconf['db'],
        user=dbconf['user'],
        passwd=dbconf['passwd'],
        charset='utf8')

    return self._conn

  def cursor(self, cursorclass = None):
    conn = self.conn()

    if cursorclass:
      return conn.cursor(cursorclass=cursorclass)

    return conn.cursor()

  def execute(self, sql, data):
    conn = self.conn()
    cursor = self.cursor()

    try:
      if type(data) is dict:
        cursor.execute(sql, data)
      else:
        cursor.executemany(sql, data)
    except Exception as e:
      try :cursor._last_executed
      except AttributeError: raise e

      print('query error: ')
      print(cursor._last_executed)

    conn.commit()
    cursor.close()

  def query(self, sql):
    from MySQLdb.cursors import SSCursor

    cursor = self.cursor(cursorclass=SSCursor)
    cursor.execute(sql)

    buff = []
    while True:
      rows = cursor.fetchmany(size=10000)
      if not rows: break
      buff += rows

    cursor.close()
    return buff


class DB_Meta(DB_Base):
  """管理下列 metadata ：
   - feed: 對應至所有資料來源 (eg, RSS, web page)，在 article 中作為 FK
   - ctlr: 對應至所有被調用過的 ctlr，在 article 中作為 FK
   - host
   - url
  """

  def __init__(self, server = 'default'):
    DB_Base.__init__(self, server)
    self.update_host_cache()
    self.update_ctlr_cache()
    self.update_feed_cache()

  #
  # Host
  # 數量有限且使用數值 id，快取避免重覆寫入
  #
  def save_host(self, host):
    cache = self._cache_host_urls
    if (host['url'] in cache): return

    # that aggressive !?
    self.update_host_cache()
    if (host['url'] in cache): return

    sql = "INSERT IGNORE INTO `hosts` (`name`, `url`) " \
      "VALUES (%(name)s, %(url)s)"

    self.execute(sql, host)
    cache.add(host['url'])

  def update_host_cache(self):
    try: self._cache_host_urls
    except AttributeError: self._cache_host_urls = set()
    sql = 'SELECT `url` FROM `hosts`'
    self._cache_host_urls.update([x[0] for x in self.query(sql)])

  #
  # feed
  # 數量有限且使用數值 id，快取避免重覆寫入
  #
  def save_feed(self, source):
    cache = self._cache_feed_urls
    if (source['url'] in cache): return

    self.update_feed_cache()
    if (source['url'] in cache): return

    sql = "INSERT IGNORE INTO `feeds` (`url`, `title`, `host_id`" \
      ") VALUES (%(url)s, %(title)s, " \
      "(SELECT `host_id` FROM `hosts` WHERE `url` = %(host_url)s))"

    self.execute(sql, source)
    cache.add(source['url'])

  def update_feed_cache(self):
    try: self._cache_feed_urls
    except AttributeError: self._cache_feed_urls = set()
    sql = 'SELECT `url` FROM `feeds`'
    self._cache_feed_urls.update([x[0] for x in self.query(sql)])

  #
  # ctlr
  # 數量有限且使用數值 id，快取避免重覆寫入
  #

  def save_ctlr(self, ctlr):
    cache = self._cache_ctlr_classnames
    if (ctlr['classname'] in cache): return

    self.update_ctlr_cache()
    if (ctlr['classname'] in cache): return

    sql = "INSERT IGNORE INTO `ctlrs` (`classname`, `created_on`" \
      ") VALUES (%(classname)s, %(created_on)s)"

    self.execute(sql, ctlr)
    cache.add(ctlr['classname'])

  def update_ctlr_cache(self):
    try: self._cache_ctlr_classnames
    except AttributeError: self._cache_ctlr_classnames = set()

    sql = 'SELECT `classname` FROM `ctlrs`'
    self._cache_ctlr_classnames.update([x[0] for x in self.query(sql)])

  def save_ctlr_feed(self, pair):
    sql = "INSERT IGNORE INTO `ctlr_feed` (" \
        "`feed_id`, `ctlr_id`" \
      ") VALUES ("\
        "(SELECT `feed_id` FROM `feeds` WHERE `url` = %(url)s), " \
        "(SELECT `ctlr_id` FROM `ctlrs` WHERE `classname` = %(classname)s)" \
      ")"

    self.execute(sql, pair)

class DB(DB_Meta):
  """管理下列目標資料 ：
   - fetch
   - response
   - article
  """

  def __init__(self, server = 'default'):
    DB_Meta.__init__(self, server)

  #
  # Fetch
  #
  def save_fetch(self, url, response, category = 'unknown'):
    """寫入 fetches 表; 不做 unique key 檢查，僅就 category 判斷是否儲存"""

    if (category in fetch_categories_ignored): return

    sql = "INSERT INTO `fetches` (`url`, `response`, `category`) VALUES" \
      "(%(url)s, %(response)s, %(category)s)"

    self.execute(sql, {"url": url, "response": response, "category": category})

  #
  # article
  #

  def list_revisits(self):
    """輸出需要 revisit 的新聞列表, 包含 meta 欄位

    @see: Ctlr_Base.do_revisit()"""
    from . import conf, Ctlr_Base

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

  #
  # Hashtbl
  # 數量可能很大，因此不做快取
  #
  def save_hashtbl(self, tbl_name, data):
    """將 data 存入列表，可以是 body, [body...] 或 [{'body':'body'}...] 的格式"""
    from . import md5
    from MySQLdb import escape_string

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

    self.execute(sql, _data)

  def save_article(self, payload):
    """更新新聞內容"""
    from json import dumps
    from datetime import datetime
    from . import md5

    # deep copy so that we don't mess up the original payload
    _payload = deepcopy(payload)
    _payload["meta"] = dumps(payload['meta'])
    _payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

    # hashtbl : html, text, meta
    _payload['html_md5'] = md5(_payload['html'])
    _payload['text_md5'] = md5(_payload['text'])
    _payload['meta_md5'] = md5(_payload['meta'])

    self.save_hashtbl('article__htmls', {
      'md5': _payload['html_md5'], 'body':_payload['html']})
    self.save_hashtbl('article__texts', {
      'md5': _payload['text_md5'], 'body':_payload['text']})
    self.save_hashtbl('article__meta', {
      'md5': _payload['meta_md5'], 'body': _payload['meta']})

    # hashtbl: url
    _payload['url_md5'] = md5(_payload['url'])
    _payload['url_read_md5'] = md5(_payload['url_read'])
    _payload['url_canonical_md5'] = md5(_payload['url_canonical'])

    self.save_hashtbl('article__urls', [
      {'md5': _payload['url_md5'], 'body': _payload['url']},
      {'md5': _payload['url_read_md5'], 'body': _payload['url_read']},
      {'md5': _payload['url_canonical_md5'], 'body': _payload['url_canonical']},
    ]);

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

    self.execute(sql, _payload)

  #
  # Response, 僅在 parse 失敗時寫入，因此積極重寫
  #

  def save_response(self, payload):
    from json import dumps
    from datetime import datetime
    from . import md5

    # deep copy so that we don't mess up the original payload
    _payload = deepcopy(payload)
    _payload["meta"] = dumps(payload['meta'])
    _payload["response_md5"] = md5(_payload['response'])

    sql = "INSERT IGNORE INTO `responses` " + \
      "(`feed_id`, `url`, `body`, `body_hash`, `meta`) VALUES(" + \
        "(SELECT `feed_id` FROM `feeds` WHERE `url` = %(feed_url)s), " + \
        "%(url)s, %(response)s, UNHEX(%(response_md5)s), %(meta)s" + \
        ")"
    self.execute(sql, _payload)
