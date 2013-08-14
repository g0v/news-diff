# -*- coding:utf-8 -*-
#
#
class Ctlr_Base:
  """
  抓取並解析單篇文章的基底類別；
  針對各種型態的新聞列表 (eg. RSS, email)，需各自實作繼承用類別
  """


  # ==============================
  # Override These
  # ==============================


  # Ctlr 生效時間
  _created_on = None

  # Ctlr 抓取目標
  _my_feeds = [
    #{"title": "要聞", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/11"},
  ]

  def parse_response(self, payload, pool, dbi):
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
  # Methods to be Overrided
  # ==============================

  def feed(self, pool, dbi):
    """在子類別中擴充並呼叫此函式, 並排程 pool """

    from datetime import datetime
    from lib import db, util

    ctlr_sig = {"classname": unicode(self.__class__)}
    if self._created_on:
      ctlr_sig['created_on'] = util.dt.to_date(self._created_on)
    else:
      ctlr_sig['created_on'] = datetime.utcnow()

    db.save_host(self.get_host(), dbi = dbi)
    db.save_ctlr(ctlr_sig, dbi = dbi)

  # ==============================
  # Procedural
  # ==============================

  def dispatch_response(self, payload, pool, dbi):
    """
    處理 fetcher 傳回之資料，調用 parse_response 解析其內容並儲存。

    輸入 payload 格式為 {
      'src': 'RESPONSE_BODY',
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
    from lib import logger, util, db
    from lib.util.dt import to_timestamp
    from lib.util.text import to_unicode

    try: payload['pub_ts'] = to_timestamp(payload['meta']['pub_date'])
    except KeyError: pass

    # dom tree 前處理
    try:
      html = lxml.html.fromstring(payload['src']) # lxml handles html encoding
      payload['src'] = to_unicode(payload['src']) # conver to unicode before storing
    except:
      extra = {'classname': self.__class__}
      logger.warning("HTML parse error, url: %s", payload['url_read'], extra=extra)
      logger.warning("Got: %s", payload['src'], extra=extra)
      pool.log_stats('error_parse')
      return

    # canonical url
    url_canonical = html.cssselect('link[rel=canonical]')
    payload['url_canonical'] = url_canonical[0].attrib['href'] \
      if len(url_canonical) > 0 else payload['url_read']

    # 移除 charset 因為保證是 unicode; 若未移除反而可能使 html parser 誤判
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
      db.save_article(article, dbi = dbi)
      pool.log_stats('done_article')
    else:
      # TODO: 還是寫入 article 表
      db.save_response(payload, dbi = dbi)
      pool.log_stats('error_parse')

  def _decorate_article(self, article):
    """在 parse_response 後執行，後處理其輸出"""

    # html post-process
    from lxml.html import tostring, fromstring
    from bs4 import BeautifulSoup
    from lib.util.net import normalize_url
    from lib.util.text import pack_string

    # article['content'] may be list of lxml doms
    if type(article['content']) is list:
      article['content'] = \
        fromstring('\n'.join([tostring(x, encoding=unicode) for x in article['content']]))

    # remove unwanted tags
    self.css_sel_drop_tree(article['content'], ['script'])

    # prettify html with BeautifulSoup
    html_bs4 = BeautifulSoup(tostring(article['content'], encoding=unicode)).body.next

    article['text'] = pack_string(html_bs4.text)
    article['html'] = pack_string(unicode(html_bs4))
    article["ctlr_classname"] = str(self.__class__)

    article['url'] = normalize_url(article['url'])
    article['url_read'] = normalize_url(article['url_read'])
    article['url_canonical'] = normalize_url(article['url_canonical'])

    self.move_out_of_meta(article, 'title')

    return article

  # ==============================
  # Utilities
  # ==============================
  def get_host(self):
    import importlib
    module_name = str(self.__class__).rsplit('.', 2)[0]
    ns = importlib.import_module(module_name)
    return ns.host

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

  # ==============================
  #
  # ==============================

  @staticmethod
  def css_sel_drop_tree(dom_tree, selector_list):
    """for lxml Elements"""
    for x in dom_tree.cssselect(", ".join(selector_list)):
      x.drop_tree()

