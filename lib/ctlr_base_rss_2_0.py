# -*- encoding: utf-8 -*-

from xml.dom import minidom
from ctlr_base import Ctlr_Base

class Ctlr_Base_RSS_2_0 (Ctlr_Base):
  """
  透過 RSS 建立清單的基底類別
  """

  # ==============================
  # Configs to be overrided
  # ==============================

  # file format, override if necessary
  _parser = {
    "format": "rss_2_0",
    "holder": 'item',
    "extracts": {
      "title": {"key": "title"},
      "link": {"key": "url"},
      "pubDate": {"key": "pub_date"}
    }
  }

  # ==============================
  # Implementing Abstract Methods
  # ==============================
  def run(self):
    Ctlr_Base.run(self)

    from . import Fetcher, db

    f = Fetcher()
    for rss in self._my_feeds:
      if ('title' not in rss):
        rss['title'] = None

      if ('host_url' not in rss):
        rss['host_url'] = self._my_host['url']

      db.save_feed(rss)
      db.save_ctlr_feed({
        'url': rss['url'],
        'classname': str(self.__class__)
      })

      print('Fetching from feed "%s"' % rss['url'])

      f.queue(
        rss['url'],
        self.dispatch_rss_2_0,
        category = self._parser['format'])

    f.start()

  # ==============================
  #
  # ==============================

  def dispatch_rss_2_0(self, payload):
    """解析 XML 格式的 RSS feed, 打包 meta 轉送給 fetcher 之格式為 {
      "feed_url": '',
      "title": '',
      "pub_date": ''
    }"""
    dom = minidom.parseString(payload['response'])
    output = []

    from . import Fetcher
    import urllib

    f = Fetcher()

    for entry in dom.getElementsByTagName(self._parser['holder']):
      meta = {"feed_url": payload['url']}
      for tag in self._parser['extracts']:
        txt = self.getTextByTagName(entry, tag)
        if (txt):
          key = self._parser['extracts'][tag]["key"]
          meta[key] = txt

      url = meta['url'].encode('utf-8')
      del (meta['url'])

      # 檢查 url 是否轉碼妥善 (urlencode)
      if (any(map(lambda(x): x > 127, [ord(x) for x in url]))):
        if (url.startswith('http://') or url.startswith('https://')):
          url = url[:7] + urllib.quote(url[7:])
        else:
          url = urllib.quote(url)

      f.queue(url, self.dispatch_response, category="response", meta = meta)
    f.start()

  def dispatch_cb(self, format):
    if (format == 'rss_2_0'):
      return self.dispatch_rss_2_0

    return None

  # ==============================
  # minidom
  # ==============================

  def getTextByTagName(self, node, tagName):
    return self.getText(node.getElementsByTagName(tagName)[0])

  def getText(self, node):
    text = ''
    for child in node.childNodes:
      if child.nodeType in [child.TEXT_NODE, child.CDATA_SECTION_NODE]:
        text += child.data
    return text
