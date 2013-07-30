# -*-encoding:utf-8 -*-
#
# 資料庫相關功能
# 每個 thread 需生成自身的 db instance；快取與一致性問題由資料庫處理
#
#

class DB:
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
      from lib import conf

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

  @staticmethod
  def execute(sql, data = None, dbi = None):

    if dbi is None: _dbi = DB()
    else: _dbi = dbi

    conn = _dbi.conn()
    cursor = _dbi.cursor()

    try:
      if data is None: cursor.execute(sql)
      elif type(data) is dict: cursor.execute(sql, data)
      else: cursor.executemany(sql, data)
    except Exception as e:
      print('query error: ')

      try:
        print(cursor._last_executed)
      except AttributeError:
        import traceback
        traceback.print_exc()

    conn.commit()
    cursor.close()

    if dbi is None: _dbi.disconnect()

  @staticmethod
  def query(sql, dbi = None):
    from MySQLdb.cursors import SSCursor

    if dbi is None: _dbi = DB()
    else: _dbi = dbi

    cursor = _dbi.cursor(cursorclass=SSCursor)

    try: cursor.execute(sql)
    except Exception as e:
      print(cursor._last_executed)
      raise e

    buff = []
    while True:
      rows = cursor.fetchmany(size=10000)
      if not rows: break
      buff += rows

    cursor.close()
    if dbi is None: _dbi.disconnect()

    return buff
