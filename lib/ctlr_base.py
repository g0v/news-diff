# -*- encoding:utf-8 -*-

class Ctlr_Base:
  """
  抓取並解析單篇文章的基底類別；
  針對各種型態的新聞列表 (eg. RSS, email)，需各自實作繼承用類別
  """


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
  # Methods for Override
  # ==============================

  def feed(self, pool, db):
    """在子類別中擴充此函式, 以將工作排程入 pool 中"""

    from datetime import datetime

    ctlr_sig = {"classname": unicode(self.__class__)}
    if self._created_on:
      ctlr_sig['created_on'] = self.to_date(self._created_on)
    else:
      ctlr_sig['created_on'] = datetime.utcnow()

    db.save_host(self._my_host)
    db.save_ctlr(ctlr_sig)

  # ==============================
  # Ctlr Configs & Overrides
  # ==============================

  # Ctlr 生效時間
  _created_on = None

  def parse_response(self, payload, pool, db):
    """解析 fetcher 抓回之 response

    payload 之輸入為：{
      'title': '[TITLE]'
      'meta': {}
    }
    輸出為：{
      'content': 包含內文之 lxml tree
    }
    若解析失敗則回傳 False
    由 dispatch_response 儲存資料
    """
    pass

  # ==============================
  # Procedural
  # ==============================

  def dispatch_response(self, payload, pool, db):
    """
    處理 fetcher 傳回之資料，調用 parse_response 解析其內容並儲存。

    輸入 payload 格式為 {
      'response': 'RESPONSE_BODY',
      'meta': {
        'feed_url': '',
        'pub_date': 'str'
      }
    }
    輸出為 {
      'html': lxml tree
    }

    @endpoint
    """
    import lxml.html
    from lib import logger

    try: payload['pub_ts'] = Ctlr_Base.to_timestamp(payload['meta']['pub_date'])
    except KeyError: pass

    # dom tree 前處理
    try:
      html = lxml.html.fromstring(payload['response'])
    except:
      extra = {'classname': self.__class__}
      logger.warning("HTML parse error, url: %s", payload['url_read'], extra=extra)
      logger.warning("Got: %s", payload['response'], extra=extra)
      pool.log_stats('error_parse')
      return

    # canonical url
    url_canonical = html.cssselect('link[rel=canonical]')
    payload['url_canonical'] = url_canonical[0].attrib['href'] \
      if len(url_canonical) > 0 else payload['url_read']

    # 移除 charset 因為保證是 unicode
    tags = html.cssselect('meta[http-equiv=Content-Type]')
    if (len(tags) > 0):
      payload['meta']['Content-Type'] = tags[0].attrib['content']
      for x in tags: x.drop_tree()

    payload['html'] = html

    self.move_out_of_meta(payload, 'feed_url')

    article = self.parse_response(payload)

    if article:
      # parsed successfully
      self._decorate_article(article)
      db.save_article(article)
      pool.log_stats('done_article')
    else:
      db.save_response(payload)
      pool.log_stats('error_parse')

  def _decorate_article(self, article):
    """在 parse_response 後執行，後處理其輸出"""

    # html post-process
    from lxml.html import tostring, fromstring
    from bs4 import BeautifulSoup
    from lib.util import normalize_url

    #remove unwanted tags
    self.css_sel_drop_tree(article['content'], ['script'])

    #prettify html with BeautifulSoup
    article['content'] = BeautifulSoup(tostring(article['content'])).body.next

    article['text'] = self.pack_string(article['content'].text)
    article['html'] = self.pack_string(unicode(article['content']))
    article["ctlr_classname"] = str(self.__class__)

    article['url'] = normalize_url(article['url'])
    article['url_read'] = normalize_url(article['url_read'])
    article['url_canonical'] = normalize_url(article['url_canonical'])

    del article['response']
    del article['content']

    self.move_out_of_meta(article, 'title')

    return article

  # ==============================
  # Utilities
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

    mytype = type(value)

    if mytype is int or mytype is float:
      # interpret as timestamp, utc
      return datetime(value)

    if mytype is datetime:
      return value

    dt = parser.parse(value)
    return dt

  @staticmethod
  def to_timestamp(value):
    mytype = type(value)
    if mytype is int or mytype is float:
      return value

    import time
    return time.mktime(Ctlr_Base.to_date(value).utctimetuple())

  @staticmethod
  def pack_string(input):
    """去除字串中對人閱讀無用的字符"""
    import re
    output = re.sub('\r', '\n', input)
    output = re.sub('\n+', '\n', output)
    output = re.sub('\s+', ' ', output)
    return output.strip()

  # ==============================
  #
  # ==============================

  @staticmethod
  def css_sel_drop_tree(dom_tree, selector_list):
    """for lxml Elements"""
    for x in dom_tree.cssselect(", ".join(selector_list)):
      x.drop_tree()

