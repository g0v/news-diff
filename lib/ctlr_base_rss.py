# -*- encoding: utf-8 -*-
from xml.dom import minidom

from ctlr_base import Ctlr_base
class Ctlr_base_RSS (Ctlr_base):
  """Controller base class from RSS
  Serves utility methods and function templates"""

  name = "Default Ctlr RSS"

  # ==============================
  # Configs
  # ==============================

  # RSS URL
  _rss_url = ''

  # file format
  _format_src = 'xml'

  # content path
  _content_tag_name = 'item'

  # tags to extract
  _extract_list = {
    "title": "title",
    "link": "url",
    "pubDate": "pub_date"
  }

  def parse_xml(self, payload):
    """解析 XML 格式的 RSS feed"""
    dom = minidom.parseString(payload['content'])
    output = []

    from . import Fetcher
    f = Fetcher()

    for entry in dom.getElementsByTagName(self._content_tag_name):
      parsed = {}
      for tag in self._extract_list:
        tmp = self.getTextByTagName(entry, tag)
        if (tmp):
          parsed[self._extract_list[tag]] = tmp

      f.queue(parsed['url'], self.parse_article, parsed = parsed)

    f.start()

  def getTextByTagName(self, node, tagName):
    return self.getText(node.getElementsByTagName(tagName)[0])

  def getText(self, node):
    text = ''
    for child in node.childNodes:
      if child.nodeType in [child.TEXT_NODE, child.CDATA_SECTION_NODE]:
        text += child.data
    return text

  def parse_cb(self, format):
    if (format == 'xml'):
      return self.parse_xml

    return None

  def run(self):
    from . import Fetcher
    f = Fetcher()
    f.queue(self._rss_url, self.parse_cb(self._format_src))
    f.start()
    pass
