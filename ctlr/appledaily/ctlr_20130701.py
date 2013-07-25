# -*- encoding: utf-8 -*-
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _created_on = '2013-07-25T16:33:26'
  _my_feeds = [
    {"title": "即時社會", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/102"},
    {"title": "即時生活", "url": "http://www.appledaily.com.tw/rss/create/kind/rnews/type/105"},
    {"title": "即時政治", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/101"},
    {"title": "即時國際", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/103"},
    {"title": "即時財經", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/104"},
    {"title": "即時體育", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/107"},
    {"title": "即時消費", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/110"},

    {"title": "國際", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/sec/type/1697"},
    {"title": "社會", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/sec/type/1066"},
    {"title": "生活", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/sec/type/2724"},
    {"title": "地方綜合", "url": "http://www.appledaily.com.tw/rss/newcreate/kind/sec/type/1076"},
    {"title": "政治", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/151"},

    {"title": "要聞", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/11"},
    {"title": "頭條", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/1077"},
  ]

  def parse_response(self, payload):
    content = payload['html'].cssselect(".abdominis .articulum")

    if content is None or len(content) == 0: return None
    content = content[0]

    self.css_sel_drop_tree(content, ['a[href^=mailto]'])

    payload['content'] = content
    return payload
