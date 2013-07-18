# -*- encoding:utf-8 -*-

class Ctlr_Base:
  """
  抓取並解析單篇文章的基底類別；
  針對各種型態的新聞列表 (eg. RSS, email)，需各自實作繼承用類別
  """
  # ==============================
  # Configs for Implementing Ctlr
  # ==============================

  # Ctlr 生效時間
  _date_online = 0

  # Ctlr 失效時間
  _date_expire = None

  # ==============================
  # Configs for Base Ctlrs
  # ==============================

  # Controller definition
  _my_host = {
    # "name": "蘋果日報",
    # "url": "http://www.appledaily.com.tw/",
  }

  _my_feeds = [
    #{"title": "要聞", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/11"},
  ]

  # ==============================
  # Abstract Methods
  # ==============================

  def run(self):
    """在子類別中覆蓋此函式, 並將抓出的文章內容以 payload
    型式傳至 dispatch_article """
    pass

  def parse_response(self, payload):
    """解析 fetcher 抓回之 response

    輸出之 article 需包含下列欄位：{
      'title': '[TITLE]'
      'text': '[TEXT]'
      'html': '[HTML]',
    }

    若解析失敗則回傳 False，由 dispatch_response 儲存
    """
    pass
  # ==============================
  #
  # ==============================

  def __init__(self):
    # @todo : date values
    pass

  def _decorate_article(self, article):
      del article['response']

      Ctlr_Base.move_out_of_meta(article, 'title')

      article['meta']["status"] = "article"
      article["text_md5"] = Ctlr_Base.md5(article['text'].encode('utf-8'))
      article["html_md5"] = Ctlr_Base.md5(article['html'].encode('utf-8'))
      article["ctlr_classname"] = str(self.__class__)
      return article

  def dispatch_response(self, payload):
    """
    處理單則新聞 response 的 callback

    對 payload 進行前處理，調用 parse_article 解析其內容，並儲存輸出結果。
    """
    from . import db

    try:
      payload['pub_ts'] = Ctlr_Base.to_timestamp(payload['meta']['pub_date'])
    except KeyError: pass

    # Keep in meta so it's passed to content.meta
    payload['url_rss'] = payload['meta']['url_rss']

    article = self.parse_response(payload)

    if article:
      # parsed successfully
      self._decorate_article(article)
      db.save_article(article)
    else:
      payload["response_md5"] = Ctlr_Base.md5(payload['response'])
      db.save_response(payload)

  @staticmethod
  def dispatch_catchup(self, payload):
    """處理前次解析失敗的資料"""
    raise Exception('Not Implemented, yet')

  @staticmethod
  def dispatch_revisit(self, payload):
    """處理 revisit 取得之資料"""

    article = self.parse_response(payload)
    if not article:
      payload["response_md5"] = Ctlr_Base.md5(payload['response'])
      return db.save_response(payload)

    self._decorate_article(article)
    db.save_revisit(article)

  # ==============================
  # Utilities
  # ==============================

  @staticmethod
  def md5(unicode_str):
    from hashlib import md5
    return md5(unicode_str).hexdigest()

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
    return time.mktime(Ctlr_Base.to_date(value).utctimetuple())
