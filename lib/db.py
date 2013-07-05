# -*-encoding:utf-8 -*-
from copy import deepcopy

class DB:
  """提供資料庫操作之 singleton，透過 DB.forge() 取得 _instance

  包含下列資料：
   - fetch: 處理透過 fetcher 抓下的資料，轉存至 fetches 表
   - indexor: 對應至所有資料來源 (eg, RSS, web page)，在 article 中作為 FK
   - parser: 對應至所有被調用過的 Parser，在 article 中作為 FK
   - article
   - content
  """

  # 當待寫入 row 到達 _min_row 時才寫入
  min_buffered_rows = 50

  # 測試模式，禁止寫入 DB
  ignore_db_write = False

  # ==============================
  # Singleton
  # ==============================
  _instance = None

  def __init__(self):
    self._conn = None
    self._cursor = None
    self.connect()

    # class variables

    self._buff_hosts = []
    self.update_host_cache ()

    self._buff_indexors = []
    self.update_indexor_cache()

    self._buff_parsers = []
    self._buff_indexor_parser = []
    self.update_parser_cache()

    self._buff_fetch = []

    self._buff_articles = []
    self._buff_article_responses = []

    self._buff_contents = []
    self._buff_content_texts = []
    self._buff_content_htmls = []

  @classmethod
  def forge(self):
    if self._instance is None:
      self._instance = DB()
    return self._instance

  # ==============================
  # Data Manip Utils
  # ==============================

  def _will_execute(self, rows, force_commit= False):
    if (self.ignore_db_write):
      return False

    if not force_commit:
      if len(rows) < self.min_buffered_rows:
        return False

    return True

  def _execute(self, sql, rows, force_commit = False):
    """將 rows (list of dict) 套用至 sql，用於寫入資料。
    若需要寫入，則清空 rows 並將其中資料回傳"""

    if (not self._will_execute(rows, force_commit)):
      return []

    _rows = deepcopy(rows)
    rows[:] = []

    try:
      self.connect()
      self._cursor.executemany(sql, _rows)
      self._conn.commit()
    except Exception:
      print(self._cursor._last_executed)

    return _rows

  def _load_into_list(self, sql):
    """取出資料表內容為 list(tuple)"""
    self.connect()
    self._cursor.execute(sql)

    buff = []
    while True:
      rows = self._cursor.fetchmany(size=10000)
      if not rows: break
      buff += rows

    return buff

  def _update_hashtbl(self, tbl_name, data, columns = ['body', 'hash'], key = 'hash'):
    """更新 hash table 類的表格; 會檢查 hash 是否重覆才寫入"""
    # escape
    tbl_name = self._conn.escape_string(tbl_name)
    key = self._conn.escape_string(key)
    columns = [self._conn.escape_string(x) for x in columns]

    self.connect()

    sql = "SELECT `%s` FROM `%s` WHERE `%s` IN (%s)" % (
      key, tbl_name, key,
      ','.join([self._conn.escape(x[key]) for x in data])
    )
    self._cursor.execute(sql)
    hashes_found = self._cursor.fetchall()

    sql = 'INSERT IGNORE INTO `%s` (%s) VALUES (' % (
      tbl_name,
      ','.join([('`%s`' % x) for x in columns])
    )
    sql += ','.join([('%(' + x + ')s') for x in columns])
    sql += ')'

    self._cursor.executemany(
      sql,
      [x for x in data if (x[key], ) not in hashes_found]
    )
    self._conn.commit()

  # ==============================
  # Data Manip
  # ==============================

  #
  # Fetch
  #
  def save_fetch(self, url, response, category = None):
    """寫入 fetches 表; 不做 unique key 檢查，僅就 category 判斷是否儲存"""
    # 不儲存的 categoruies
    categories_ignored = [None, 'article']

    if (category not in categories_ignored):
      self._buff_fetch.append({"url": url, "response": response})

    self.commit_fetch()

  def commit_fetch(self, force_commit = False):
    sql = "INSERT INTO `fetches` (`url`, `response`) VALUES(%(url)s, %(response)s)"
    self._execute(sql, self._buff_fetch, force_commit)

  #
  # Article, 僅在 parse 失敗時寫入，因此積極重寫
  #

  def save_article(self, _payload):
    from json import dumps
    from datetime import datetime
    from . import Ctlr_Base

    # deep copy so that we don't mess up the original payload
    payload = deepcopy(_payload)
    payload["meta"] = dumps(payload['meta'])
    payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

    self._buff_articles.append(payload)
    self.commit_articles()

  def commit_articles(self, force_commit = 0):
    buff = self._buff_articles

    if (not self._will_execute(buff, force_commit)):
      return

    # Update FK
    self.commit_indexors(1)

    sql = "INSERT IGNORE INTO `articles` " + \
      "(`indexor_id`, `url`, `pub_ts`, `title`, `response`, `response_md5`, `meta`) VALUES(" + \
        "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(url_rss)s), " + \
        "%(url)s, %(pub_ts)s, %(title)s, %(response)s, %(response_md5)s, %(meta)s" + \
        ")"
    written = self._execute(sql, buff, force_commit)

  #
  # Content
  #

  def save_content(self, _payload):
    from json import dumps
    from datetime import datetime
    from . import Ctlr_Base

    buff = self._buff_contents

    # 同批抓到同樣內容，不考慮是否變動，直接忽略
    if any([x['text_md5'] == _payload['text_md5'] and x['url'] == _payload['md5'] for x in buff]):
      return

    # deep copy so that we don't mess up the original payload
    payload = deepcopy(_payload)
    payload["meta"] = dumps(payload['meta'])
    payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

    buff.append(payload)
    self.commit_contents()

  def commit_contents(self, force_commit = 0):
    """更新新聞內容；由於要持續更新 updated_on，因此不做快取
    @todo: 檢查是否已有同樣內容 (url, content_id)，決定使用 update or insert"""
    buff = self._buff_contents

    if (not self._will_execute(buff, force_commit)):
      return

    # Update FK
    self.commit_indexors(1)
    self.commit_parsers(1)

    # update content text & html
    self._update_hashtbl('content_htmls', [{"hash": x['html_md5'], "body": x['html']} for x in buff])
    self._update_hashtbl('content_texts', [{"hash": x['text_md5'], "body": x['text']} for x in buff])

    # do the insert
    sql = "INSERT INTO `contents` (" \
        "`pub_ts`, `created_on`, `indexor_id`, `parser_id`, `url`, `title`, " \
        "`meta`, `html_id`, `text_id`" \
      ") VALUES(" \
        "%(pub_ts)s, CURRENT_TIMESTAMP, " \
        "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(url_rss)s), " \
        "(SELECT `parser_id` FROM `parsers` WHERE `classname` = %(parser_classname)s), " \
        "%(url)s, %(title)s, %(meta)s, " \
        "(SELECT `html_id` FROM `content_htmls` WHERE `hash` = %(html_md5)s), " \
        "(SELECT `text_id` FROM `content_texts` WHERE `hash` = %(text_md5)s)" \
      ") ON DUPLICATE KEY UPDATE last_seen_on = CURRENT_TIMESTAMP"

    written = self._execute(sql, self._buff_contents, force_commit)

  #
  # Host
  # 數量有限且不多，因此使用 cache 避免重覆寫入
  #

  def save_host(self, host):
    buff = self._buff_hosts
    cache = self._cache_host_urls

    if ((host['url'],) not in cache):
      if (not any([x['url'] == host['url'] for x in buff])):
        buff.append(host)

    self.commit_hosts()

  def commit_hosts(self, force_commit = 0):
    buff = self._buff_hosts
    cache = self._cache_host_urls

    if (not self._will_execute(buff, force_commit)):
      return

    sql = "INSERT IGNORE INTO `hosts` (`name`, `url`" \
      ") VALUES (%(name)s, %(url)s)"
    written = self._execute(sql, buff, force_commit)

    # Update cache
    cache[:] = list(set(
      cache +
      map(lambda x: (x['url'], ), written)))

  def update_host_cache(self):
    sql = 'SELECT `url` FROM `hosts`'
    self._cache_host_urls = self._load_into_list(sql)

  #
  # Indexor
  #

  def save_indexor(self, source):
    buff = self._buff_indexors
    cache = self._cache_indexor_urls

    if ((source['url'],) not in cache):
      if (not any([x['url'] == source['url'] for x in buff])):
        buff.append(source)

    self.commit_indexors()

  def commit_indexors(self, force_commit = 0):
    buff = self._buff_indexors
    cache = self._cache_indexor_urls

    if (not self._will_execute(buff, force_commit)):
      return
    self.commit_hosts(1)

    sql = "INSERT IGNORE INTO `indexors` (`url`, `title`, `host_id`" \
      ") VALUES (%(url)s, %(title)s, " \
      "(SELECT `host_id` FROM `hosts` WHERE `url` = %(host_url)s))"
    written = self._execute(sql, buff, force_commit)

    # Update cache
    cache[:] = list(set(
      cache +
      map(lambda x: (x['url'], ), written)))

  def update_indexor_cache(self):
    sql = 'SELECT `url` FROM `indexors`'
    self._cache_indexor_urls = self._load_into_list(sql)

  #
  # Parser
  #

  def save_parser(self, parser):
    buff = self._buff_parsers
    cache = self._cache_parser_classnames

    if ((parser['classname'],) not in cache):
      if (not any([x['classname'] == parser['classname'] for x in buff])):
        buff.append(parser)

    self.commit_indexor_parser()

  def save_indexor_parser(self, pair):
    buff = self._buff_indexor_parser

    if (not pair in buff):
      buff.append(pair)

    self.commit_indexor_parser()

  def commit_parsers(self, force_commit = 0):
    buff = self._buff_parsers
    cache = self._cache_parser_classnames

    if (not self._will_execute(buff, force_commit)):
      return

    sql = "INSERT IGNORE INTO `parsers` (`classname`" \
      ") VALUES (%(classname)s)"
    written = self._execute(sql, buff, force_commit)

    # Update cache
    cache[:] = list(set(
      cache +
      map(lambda x: (x['classname'], ), written)))

  def commit_indexor_parser(self, force_commit = 0):
    buff = self._buff_indexor_parser

    if (not self._will_execute(buff, force_commit)):
      return

    self.commit_indexors(1)
    self.commit_parsers(1)

    sql = "INSERT IGNORE INTO `indexor_parser` (" \
        "`indexor_id`, `parser_id`" \
      ") VALUES ("\
        "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(url)s), " \
        "(SELECT `parser_id` FROM `parsers` WHERE `classname` = %(classname)s)" \
      ")"

    written = self._execute(sql, buff, force_commit)

  def update_parser_cache(self):
    sql = 'SELECT `classname` FROM `parsers`'
    self._cache_parser_classnames = self._load_into_list(sql)

  # ==============================
  # Connection
  # ==============================
  def connect(self, server = 'default'):
    if (not (self._conn and self._conn.open)):
      import MySQLdb
      from MySQLdb.cursors import SSCursor
      from . import conf

      dbconf = conf['db'][server]

      self._conn = MySQLdb.connect(
        host=dbconf['host'],
        db=dbconf['db'],
        user=dbconf['user'],
        passwd=dbconf['passwd'],
        charset='utf8')

      # todo: 若 conn 未被重設, 需要 close 舊 cursor ?
      self._cursor = self._conn.cursor(cursorclass=SSCursor)

  def flush(self):
    self.commit_indexor_parser(1)

    # called from above
    #self.commit_indexors(1)
    #self.commit_parsers(1)
    # called from commit_indexors()
    #self.commit_hosts(1)

    self.commit_fetch(1)
    self.commit_articles(1)
    self.commit_contents(1)

  def disconnect(self):
    self.flush()

    self._cursor.close()
    self._cursor = None
    self._conn.close()
    self._conn = None
