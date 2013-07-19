# -*- encoding: utf-8 -*-
from .. import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _my_host = {
    "name": "自由時報",
    "url": "http://www.libertytimes.com.tw/",
  }

  _my_feeds = [
    {"title": "焦點新聞", "url": "http://www.libertytimes.com.tw/rss/fo.xml"},
    {"title": "政治新聞", "url": "http://www.libertytimes.com.tw/rss/p.xml"},
    {"title": "生活新聞", "url": "http://www.libertytimes.com.tw/rss/life.xml"},
    {"title": "國際新聞", "url": "http://www.libertytimes.com.tw/rss/int.xml"},
    {"title": "社會新聞", "url": "http://www.libertytimes.com.tw/rss/so.xml"},
    {"title": "體育新聞", "url": "http://www.libertytimes.com.tw/rss/sp.xml"},
    {"title": "財經焦點", "url": "http://www.libertytimes.com.tw/rss/e.xml"},
  ]

  def parse_response(self, payload):
    # @todo : bypass feedsportal
    content = payload['html'].cssselect('#newsContent')

    if content is None or len(content) == 0: return None
    content = content[0]

    payload['content'] = content
    return payload
