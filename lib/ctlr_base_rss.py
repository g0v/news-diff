# -*- encoding: utf-8 -*-
from xml.dom import minidom
from ctlr_base import Ctlr_Base

class Ctlr_Base_RSS (Ctlr_Base):
  """
  透過 RSS 建立清單的基底類別
  """

  # ==============================
  # Configs to be overrided
  # ==============================

  # Controller definition
  _my_host = {
    # "name": "蘋果日報",
    # "url": "http://www.appledaily.com.tw/",
  }

  _my_feeds = [
    #{"title": "要聞", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/11"},
  ]

  # file format, override if necessary
  _parser = {
    "format": "rss2_0",
    "holder": 'item',
    "extracts": {
      "title": {"key": "title"},
      "link": {"key": "url"},
      "pubDate": {"key": "pub_date"}
    }
  }

  # ==============================
  #
  # ==============================

  def dispatch_rss2_0(self, payload):
    """解析 XML 格式的 RSS feed"""
    dom = minidom.parseString(payload['response'])
    output = []

    from . import Fetcher
    f = Fetcher()

    for entry in dom.getElementsByTagName(self._parser['holder']):
      meta = {"url_rss": payload['url']}
      for tag in self._parser['extracts']:
        txt = self.getTextByTagName(entry, tag)
        if (txt):
          key = self._parser['extracts'][tag]["key"]
          meta[key] = txt

      url = meta['url']
      del (meta['url'])

      f.queue(url, self.dispatch_article, category="article", meta = meta)
    f.start()

  def dispatch_cb(self, format):
    if (format == 'rss2_0'):
      return self.dispatch_rss2_0

    return None

  def run(self):
    from . import Fetcher, db

    db.save_host(self._my_host)

    f = Fetcher()
    for rss in self._my_feeds:
      if ('title' not in rss):
        rss['title'] = None

      if ('host_url' not in rss):
        rss['host_url'] = self._my_host['url']

      db.save_parser({"classname": str(self.__class__)})
      db.save_indexor(rss)
      db.save_indexor_parser({
        'url': rss['url'],
        'classname': str(self.__class__)
      })

      f.queue(
        rss['url'],
        self.dispatch_cb(self._parser['format']),
        category = "rss")

    f.start()

  # ==============================
  # minidom related
  # ==============================

  def getTextByTagName(self, node, tagName):
    return self.getText(node.getElementsByTagName(tagName)[0])

  def getText(self, node):
    text = ''
    for child in node.childNodes:
      if child.nodeType in [child.TEXT_NODE, child.CDATA_SECTION_NODE]:
        text += child.data
    return text
