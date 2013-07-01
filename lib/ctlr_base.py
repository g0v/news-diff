# -*- encoding:utf-8 -*-

class Ctlr_base:
  """
  抓取並解析單篇文章的基底類別

  調用流程：
    news-diff.py
    run()
    dispatch_article() :
    parse_article() :
  """
  # ==============================
  # Controller Configs
  # ==============================
  _date_online = 0
  _date_expire = None

  # ==============================
  #
  # ==============================
  def parse_article(self, payload):
    """在類別中覆蓋此函式以建立操作邏輯"""
    del(payload['response'])
    #print(payload)

  def run(self):
    """在類別中覆蓋此函式以建立操作邏輯"""
    pass

  # ==============================
  #
  # ==============================

  def __init__(self):
    # date values
    pass

  def dispatch_article(self, payload):
    """
    處理單則新聞的 callback

    調整 meta 內外的資訊，並轉發由 parse_article 分析與儲存。
    """

    try:
      payload['pub_ts'] = Ctlr_base.to_timestamp(payload['meta']['pub_date'])
    except Error: pass

    Ctlr_base.move_out_of_meta(payload, 'url_rss')
    Ctlr_base.move_out_of_meta(payload, 'title')

    from . import db
    db.save_article(payload)

    # payload['meta']['ctlr'] = str(self.__class__)
    self.parse_article(payload)

  # ==============================
  # Static utility methods
  # ==============================

  @staticmethod
  def move_into_meta(payload, key):
    try:
      payload['meta'][key] = payload[key]
      del payload[key]
    except KeyError: pass

  @staticmethod
  def move_out_of_meta(payload, key):
    try:
      payload[key] = payload['meta'][key]
      del payload['meta'][key]
    except KeyError: pass

  @staticmethod
  def to_date(value):
    """將 value 轉換為 datetime object, 包含時差資訊"""
    from dateutil import parser
    from datetime import datetime

    if type(value) is int:
      # interpret as timestamp, utc
      return datetime(value)

    if type(value) is datetime:
      return value

    dt = parser.parse(value)
    return dt

  @staticmethod
  def to_timestamp(value):
    import time
    return time.mktime(Ctlr_base.to_date(value).utctimetuple())
