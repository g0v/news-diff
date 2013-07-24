# -*- encoding:utf-8 -*-

import importlib

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

    輸出之 article 需包含下列欄位：{
      'title': '[TITLE]'
      'text': '[TEXT]'
      'html': '[HTML]',
    }

    若解析失敗則回傳 False，由 dispatch_response 儲存
    """
    pass

  # ==============================
  # Revisit
  # ==============================

  @staticmethod
  def revisit_tbl():
    return {
        #30: 0,
        180: 60,
        1440: 360,
        10080: 2880,
        43200: 20160
      }

  @staticmethod
  def revisit_max_min():
    return max(Ctlr_Base.revisit_tbl().keys())

  @staticmethod
  def need_revisit(created_on, last_seen_on):
    from datetime import datetime
    import math

    tbl = Ctlr_Base.revisit_tbl()
    now = datetime.utcnow()
    article_age = math.floor((now - created_on).total_seconds() / 60)
    visit_age = math.ceil((now - last_seen_on).total_seconds() / 60)

    tmp = filter(lambda(x): x > article_age, tbl.keys())

    if (len(tmp) == 0):
      #expired, should be filtered by DB
      return False

    interval = tbl[min(tmp)]
    return visit_age >= interval

  @staticmethod
  def do_revisit():
    """重下載必要的新聞，仿造 Base Ctlr :: dispatch_rss_2_0 meta
    並轉由 dispatch_response 處理

    @see db.list_revisits()"""

    from . import Fetcher, db
    import json

    f = Fetcher()
    ctlr_cache = {}
    revisit_list = db.list_revisits()

    print("Revisiting %d articles" % len(revisit_list))

    for x in revisit_list:
      if (x[7] not in ctlr_cache):
        (ns, cn) = x[7].rsplit('.', 1)
        module = importlib.import_module(ns)
        ctlr_cache[x[7]] = getattr(module, cn)()

      ctlr = ctlr_cache[x[7]]
      meta = json.loads(x[6])

      meta['feed_url'] = x[3]
      meta['pub_date'] = Ctlr_Base.to_timestamp(x[2])
      meta['title'] = x[5]

      f.queue(x[4], ctlr.dispatch_response, category="revisit", meta = meta)

    f.start()

  @staticmethod
  def do_fetch(ctlr_list):
    for pkg in ctlr_list:
      module = importlib.import_module('lib.%s' % pkg)

      for ctlr in module.Ctlrs:
        ctlr().run()

  # ==============================
  # Procedural
  # ==============================

  def dispatch_response(self, payload, pool, db):
    """
    處理 fetcher 傳回之資料，調用 parse_article 解析其內容並儲存。

    輸入 payload 格式為 {
      'response': 'RESPONSE_BODY',
      'meta': {
        'feed_url': '',
        'pub_date': 'str'
      }
    }

    """
    import lxml.html

    try:
      payload['pub_ts'] = Ctlr_Base.to_timestamp(payload['meta']['pub_date'])
    except KeyError: pass

    # Keep in meta so it's passed to content.meta
    # payload['feed_url'] = payload['meta']['feed_url']
    #
    # Don't keep it, track feed_id instead
    self.move_out_of_meta(payload, 'feed_url')

    payload['html'] = lxml.html.fromstring(payload['response'])
    article = self.parse_response(payload)

    if article:
      # parsed successfully
      self._decorate_article(article)
      db.save_article(article)
    else:
      payload["response_md5"] = Ctlr_Base.md5(payload['response'])
      db.save_response(payload)

  def _decorate_article(self, article):
    """在 parse_response 後執行"""

    # html post-process
    import re
    from lxml.html import tostring, fromstring
    from bs4 import BeautifulSoup

    #update article url with canonical url
    canonical_url = fromstring(article['response']).cssselect('link[rel=canonical]')
    if (len(canonical_url) > 0):
      article['url'] = canonical_url[0].attrib['href']

    #remove unwanted tags
    self.css_sel_drop_tree(article['content'], ['script'])

    #prettify html with BeautifulSoup
    article['content'] = BeautifulSoup(tostring(article['content'])).body.next

    article["status"] = "article"
    article['text'] = self.squeeze_string(article['content'].text)
    article["text_md5"] = Ctlr_Base.md5(article['text'].encode('utf-8'))
    article['html'] = self.squeeze_string(unicode(article['content']))
    article["html_md5"] = Ctlr_Base.md5(article['html'].encode('utf-8'))
    article["ctlr_classname"] = str(self.__class__)

    Ctlr_Base.move_out_of_meta(article, 'title')

    del article['response']
    del article['content']

    return article

  def dispatch_catchup(self, payload):
    """處理 responses 中解析失敗的資料"""
    raise Exception('Not Implemented, yet')

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
  def squeeze_string(input):
    import re
    output = re.sub('\r', '\n', input)
    output = re.sub('\n+', '\n', output)
    output = re.sub('\s+', ' ', output)
    return output.strip()

  # ==============================
  #
  # ==============================

  @staticmethod
  def css_sel_drop_tree(element, selector_list):
    """for lxml Elements"""
    for x in element.cssselect(", ".join(selector_list)):
      x.drop_tree()
