# -*-encoding:utf-8 -*-
import MySQLdb
from MySQLdb.cursors import SSCursor

class DB:
  """資料庫存取 singleton"""
  # ==============================
  # Singleton-related
  # ==============================
  _instance = None

  def __init__(self):
    self._conn = None
    self._cursor = None
    self.connect()

    self._buff_fetch = []

    self._buff_indexor = []
    self.update_indexor_cache()

    self._buff_parser = []
    self.update_parser_cache()

    self._buff_article = []
    self.update_article_cache()

  @classmethod
  def forge(self):
    if self._instance is None:
      self._instance = DB()
    return self._instance

  # ==============================
  # Data Manip
  # ==============================
  #
  # Fetch
  #
  def save_fetch(self, url, response):
    self._buff_fetch.append({"url": url, "response": response})
    self.commit_fetch()

  def commit_fetch(self, force_commit = 0):
    # consider do it later
    if (0 and not force_commit):
      return

    self.connect()
    sql = "INSERT INTO `fetches` (`url`, `response`) VALUES(%(url)s, %(response)s)"
    buff = self._buff_fetch
    self._buff_fetch = []
    self._cursor.executemany(sql, buff)
    self._conn.commit()

  #
  # Article
  #
  def update_article_cache(self):
    self.connect()
    self._cursor.execute('SELECT `response_md5`, `url` FROM `articles`')

    buff = []
    while True:
      rows = self._cursor.fetchmany(size=10000)
      if not rows:
        break
      buff += rows

    self._cached_articles = buff
    print(self._cached_articles)

  def save_article(self, _payload):
    from md5 import md5
    from copy import deepcopy
    from json import dumps
    from datetime import datetime
    from . import Ctlr_base

    payload = deepcopy(_payload)
    payload["meta"] = dumps(payload['meta'])
    payload["response_md5"] = md5(payload['response']).hexdigest()
    payload["pub_ts"] = datetime.fromtimestamp(payload["pub_ts"]).isoformat()

    self.save_indexor(payload['url_rss'])

    if ((payload["response_md5"], payload["url"]) not in self._cached_articles):
      self._buff_article.append(payload)

    self.commit_article()

  def commit_article(self, force_commit = 0):
    # consider do it later
    if (0 and not force_commit):
      return

    self.connect()
    self.commit_indexor(1)

    buff = self._buff_article
    self._buff_article = []

    sql = "INSERT INTO `articles` " + \
      "(`indexor_id`, `url`, `pub_ts`, `title`, `meta`, `response`, `response_md5`) VALUES(" + \
        "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(url_rss)s), " + \
        "%(url)s, %(pub_ts)s, %(title)s, %(meta)s, %(response)s, %(response_md5)s" + \
        ") ON DUPLICATE KEY UPDATE `updated_on` = CURRENT_TIMESTAMP"
    self._cursor.executemany(sql, buff)
    self._conn.commit()

    self._cached_articles = list(set(
      self._cached_articles +
      map(lambda x: (x['response_md5'], x['url']), buff)))
  #
  # Indexor
  #
  def update_indexor_cache(self):
    self.connect()
    self._cursor.execute('SELECT `url` FROM `indexors`')

    buff = []
    while True:
      rows = self._cursor.fetchmany(size=10000)
      if not rows:
        break

      buff += rows

    self._cached_indexor_urls = map(lambda x: x[0], buff)

  def save_indexor(self, url):
    if (url not in self._cached_indexor_urls):
      self._buff_indexor.append({"url": url})

    self.commit_indexor()

  def commit_indexor(self, force_commit = 0):
    # consider do it later
    if (0 and not force_commit):
      return

    self.connect()

    buff = self._buff_indexor
    self._buff_indexor = []

    sql = "INSERT IGNORE INTO `indexors` (`url`) VALUES(%(url)s)"
    self._cursor.executemany(sql, buff)
    self._conn.commit()

    self._cached_indexor_urls = list(set(
      self._cached_indexor_urls +
      map(lambda x: x['url'], buff)))

  #
  # Parser
  #
  def update_parser_cache(self):
    self.connect()
    self._cursor.execute('SELECT `classname` FROM `parsers`')

    buff = []
    while True:
      rows = self._cursor.fetchmany(size=10000)
      if not rows:
        break

      buff += rows
    self._cached_indexor_urls = map(lambda x: x[0], buff)

  def save_parser(self, indexor_url, classname):
    if (classname not in self._cached_parser_classnames):
      self._buff_parser.append({"indexor_url": indexor_url, "classname": classname})

    self.commit_parser()

  def commit_parser(self, force_commit = 0):
    # consider do it later
    if (0 and not force_commit):
      return

    self.connect()
    self.commit_indexor(1)

    buff = self._buff_parser
    self._buff_parser = []

    sql = "INSERT IGNORE INTO `parsers` (`indexor_id`, `classname`) VALUES" + \
      "(SELECT `indexor_id` FROM `indexors` WHERE `url` = %(indexor_url)s), %(classname)s)"
    self._cursor.executemany(sql, buff)
    self._conn.commit()

    self._cached_parser_classnames = list(set(
      self._cached_parser_classnames +
      map(lambda x: x['classname'], buff)))

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
    self.commit_indexor(1)
    self.commit_parser(1)
    self.commit_article(1)

  def disconnect(self):
    self.flush()
    self._cursor.close()
    self._cursor = None
    self._conn.close()
    self._conn = None


