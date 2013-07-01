# -*-encoding:utf-8 -*-
import MySQLdb
from MySQLdb.cursors import SSCursor

class DB:
  """資料庫存取 singleton"""


  # ==============================
  # Data
  # ==============================
  def save_fetch(url, content, category = 'rss'):
    pass

  # ==============================
  # Connection
  # ==============================
  _conn = None
  _cursor = None

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
    print('db.flush')
    pass

  def disconnect(self):
    self.flush()
    self._cursor.close()
    self._cursor = None
    self._conn.close()
    self._conn = None

  # ==============================
  # Singleton-related
  # ==============================
  _instance = None

  def __init__(self):
    self.connect()

  @classmethod
  def forge(self):
    if self._instance is None:
      self._instance = DB()
    return self._instance

