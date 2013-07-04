# -*-encoding:utf-8 -*-
import MySQLdb
from MySQLdb.cursors import SSCursor
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

    self._buff_fetch = []

    self._buff_indexors = []
    self.update_indexor_cache()

    self._buff_articles = []
    self.update_article_cache()

    self._buff_contents = []
    self.update_content_cache()

  @classmethod
  def forge(self):
    if self._instance is None:
      self._instance = DB()
    return self._instance

  # ==============================
  # Data Manip
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

    self.connect()
    self._cursor.executemany(sql, _rows)
    self._conn.commit()

    return _rows

  def _load_as_list(self, sql):
    """取出資料表內容為 list(tuple)"""
    self.connect()
    self._cursor.execute(sql)

    buff = []
    while True:
      rows = self._cursor.fetchmany(size=10000)
      if not rows: break
      buff += rows

    return buff

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
  # Article
  #

  def save_article(self, _payload):
    from json import dumps
    from datetime import datetime
    from . import Ctlr_base

    # deep copy so that we don't mess up the original payload
    payload = deepcopy(_payload)
    payload["meta"] = dumps(payload['meta'])
    payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

    self.save_indexor(payload['url_rss'])

    if ((payload["response_md5"], payload["url"]) not in self._cache_articles):
      self._buff_articles.append(payload)

    self.commit_articles()

  def commit_articles(self, force_commit = 0):
    # Update FK
    if (self._will_execute(self._buff_articles, force_commit)):
      self.commit_indexors(1)

    sql = "INSERT IGNORE INTO `articles` " + \
      "(`indexor_id`, `url`, `pub_ts`, `title`, `meta`, `response`, `response_md5`) VALUES(" + \
        "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(url_rss)s), " + \
        "%(url)s, %(pub_ts)s, %(title)s, %(meta)s, %(response)s, %(response_md5)s" + \
        ")"
    written = self._execute(sql, self._buff_articles, force_commit)

    # Update cache
    self._cache_articles = list(set(
      self._cache_articles +
      map(lambda x: (x['response_md5'], x['url']), written)))

  def update_article_cache(self):
    sql = 'SELECT `response_md5`, `url` FROM `articles`'
    self._cache_articles = self._load_as_list(sql)

  #
  # Content
  #

  def save_content(self, _payload):
    from json import dumps
    from datetime import datetime
    from . import Ctlr_base

    # deep copy so that we don't mess up the original payload
    payload = deepcopy(_payload)
    payload["meta"] = dumps(payload['meta'])
    payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

    self.save_indexor(payload['url_rss'])

    if ((payload["content_md5"], payload["url"]) not in self._cache_contents):
      self._buff_contents.append(payload)

    self.commit_contents()

  def commit_contents(self, force_commit = 0):
    return

    # Update FK
    if (self._will_execute(self._buff_contents, force_commit)):
      self.commit_indexors(1)
      self.commit_parsers(1)

    sql = "INSERT IGNORE INTO `contents` (" \
        "`pub_ts`, `created_on`, `indexor_id`, `parser_id`, `url`, `title`, " \
        "`content_md5`, `content`, `html`, `meta`" \
      " VALUES(" \
        "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(url_rss)s), " \
        "%(url)s, %(pub_ts)s, %(title)s, %(meta)s, %(content)s, %(content_md5)s" \
        ")"
    written = self._execute(sql, self._buff_contents, force_commit)

    # Update cache
    self._cache_contents = list(set(
      self._cache_contents +
      map(lambda x: (x['content_md5'], x['url']), written)))

  def update_content_cache(self):
    sql = 'SELECT `content_md5`, `url` FROM `contents`'
    self._cache_contents = self._load_as_list(sql)

  #
  # Indexor
  #

  def save_indexor(self, url):
    if ((url,) not in self._cache_indexor_urls):
      self._buff_indexors.append({"url": url})

    self.commit_indexors()

  def commit_indexors(self, force_commit = 0):
    sql = "INSERT IGNORE INTO `indexors` (`url`) VALUES(%(url)s)"
    written = self._execute(sql, self._buff_indexors, force_commit)

    # Update cache
    try:
      self._cache_indexor_urls = list(set(
        self._cache_indexor_urls +
        map(lambda x: (x['url'], ), written)))
    except Exception:
      print(written)
      raise Exception('gj')

  def update_indexor_cache(self):
    sql = 'SELECT `url` FROM `indexors`'
    self._cache_indexor_urls = self._load_as_list(sql)

  #
  # Parser
  #


  # ==============================
  # Connection
  # ==============================
  def connect(self, server = 'default'):
    if (not (self._conn and self._conn.open)):
      import json
      from os.path import dirname, join

      with open(join(dirname(dirname(__file__)), 'conf', 'db.json'), 'r') as fp:
        dbconf = json.load(fp)[server]

      self._conn = MySQLdb.connect(
        host=dbconf['host'],
        db=dbconf['db'],
        user=dbconf['user'],
        passwd=dbconf['passwd'],
        charset='utf8')

      # todo: 若 conn 未被重設, 需要 close 舊 cursor ?
      self._cursor = self._conn.cursor(cursorclass=SSCursor)

  def flush(self):
    self.commit_fetch(1)
    self.commit_indexors(1)
    self.commit_articles(1)
    self.commit_contents(1)

  def disconnect(self):
    self.flush()

    self._cursor.close()
    self._cursor = None
    self._conn.close()
    self._conn = None
