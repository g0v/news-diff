# -*- coding: utf-8 -*-

from urllib import quote, unquote

from base import Ctlr_Base

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
      "title": {"key": "title", "callback": unquote},
      "link": {"key": "url"},
      "pubDate": {"key": "pub_date"}
    }
  }

  # ==============================
  # Implementing Abstract Methods
  # ==============================
  def feed(self, pool, dbi):
    from lib import db, logger

    Ctlr_Base.feed(self, pool, dbi)

    for rss in self._my_feeds:
      if ('title' not in rss):
        rss['title'] = None

      if ('host_url' not in rss):
        rss['host_url'] = self.get_host()['url']

      db.save_feed(rss, dbi = dbi)
      db.save_ctlr_feed({
        'url': rss['url'],
        'classname': str(self.__class__)
      }, dbi = dbi)

      logger.info('%s queued', rss['url'], extra={'classname': self.__class__})

      pool.put(rss['url'], self.dispatch_rss_2_0, category = self._parser['format'])

  # ==============================
  #
  # ==============================

  def dispatch_rss_2_0(self, payload, pool, dbi):
    """解析 XML 格式的 RSS feed, 打包 meta 轉送給 fetcher 之格式為 {
      "feed_url": '',
      "title": '',
      "pub_date": ''
    }

    @endpoint
    """
    from xml.dom import minidom

    from lib import logger, db

    try:
      dom = minidom.parseString(payload['src'])
    except:
      logger.warning('failed parsing %s', payload['url'], extra={'classname': self.__class__})
      pool.log_stats('error_parse')
      return

    proc_list = []
    urls = []

    for entry in dom.getElementsByTagName(self._parser['holder']):
      meta = {"feed_url": payload['url']}
      for tag in self._parser['extracts']:
        txt = self.getTextByTagName(entry, tag)
        if (txt):
          key = self._parser['extracts'][tag]["key"]

          if 'callback' in self._parser['extracts'][tag]:
            meta[key] = self._parser['extracts'][tag]['callback'](txt)
          else:
            meta[key] = txt

      url = meta['url'].encode('utf-8')
      del (meta['url'])

      # 檢查 url 是否轉碼妥善 (urlencode)
      if (any(map(lambda(x): x > 127, [ord(x) for x in url]))):
        if (url.startswith('http://') or url.startswith('https://')):
          url = url[:7] + quote(url[7:])
        else:
          url = quote(url)
      proc_list.append({'url': url, 'meta': meta})
      urls.append(url)

    urls = db.get_fresh_urls(urls)

    for proc in proc_list:
      if (proc['url'] in urls):
        pool.put(proc['url'], self.dispatch_response, category="response", meta = proc['meta'])
      else:
        pool.log_stats('done_skipped')
        logger.info('%s found and skipped', proc['url'], extra={'classname': self.__class__})

    pool.log_stats('done_feed')

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
