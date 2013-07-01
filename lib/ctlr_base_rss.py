# -*- encoding: utf-8 -*-
from xml.dom import minidom

from ctlr_base import Ctlr_base
class Ctlr_base_RSS (Ctlr_base):
  """
  透過 RSS 建立清單的基底類別

  調用流程：
    news-diff.py
    run()
    dispatch_xml() : 解析抓回的 RSS，並送出對文章的 request
    dispatch_article() :
    parse_article() :
  """

  # ==============================
  # Configs
  # ==============================

  # RSS URL list
  _rss_urls = []

  # file format
  _format_src = 'xml'

  # content path
  _content_tag_name = 'item'

  # 要從 RSS 中截取，透過 meta 轉送的欄位列表
  _extract_list = {
    "title": {"key": "title"},
    "link": {"key": "url"},
    "pubDate": {"key": "pub_date"}
  }

  # ==============================
  #
  # ==============================

  def dispatch_xml(self, payload):
    """解析 XML 格式的 RSS feed"""
    dom = minidom.parseString(payload['response'])
    output = []

    from . import Fetcher
    f = Fetcher()

    for entry in dom.getElementsByTagName(self._content_tag_name):
      meta = {"url_rss": payload['url']}
      for tag in self._extract_list:
        txt = self.getTextByTagName(entry, tag)
        if (txt):
          key = self._extract_list[tag]["key"]
          meta[key] = txt

      url = meta['url']
      del (meta['url'])

      f.queue(url, self.dispatch_article, meta = meta)
    f.start()

  def dispatch_cb(self, format):
    if (format == 'xml'):
      return self.dispatch_xml

    return None

  def run(self):
    from . import Fetcher
    f = Fetcher()
    for rss_url in self._rss_urls:
      f.queue(rss_url, self.dispatch_cb(self._format_src))
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
