# -*- encoding: utf-8 -*-
#
from .. import Ctlr_Base_RSS_2_0
from lxml.html import fromstring

class Ctlr(Ctlr_Base_RSS_2_0):
  """中間大圖樣版，上方有字型調整按鈕，url 無 .html"""
  _my_host = {
    "name": "中時電子報",
    "url": "http://www.chinatimes.com/",
  }

  _my_feeds = [
    {"title": "最新焦點", "url": "http://rss.chinatimes.com/rss/focusing-u.rss"},

    {"title": "重點要聞", "url": "http://www.chinatimes.com/realtimenews-focus.rss"},
    {"title": "地方掃描", "url": "http://www.chinatimes.com/realtimenews-local.rss"},

    {"title": "政治綜合", "url": "http://www.chinatimes.com/realtimenews-politic.rss"},
    {"title": "國際情報", "url": "http://www.chinatimes.com/realtimenews-international.rss"},
  ]

  def parse_response(self, payload):
    content = payload['html'].cssselect('.page_container > article')

    if content is None or len(content) == 0: return None
    content = content[0]

    self.css_sel_drop_tree(content, [
        'nav.nav-below', '.page_index', '.read_later', '.socialshare',
        '#penbi', '#disqus', '.article_star', '.article_function',
        '.a_f_star', '.page_ad', '.disqus_box', '.share_icon', '.share_media'
      ])

    payload['content'] = content
    return payload

class Ctlr2(Ctlr_Base_RSS_2_0):
  """多文字樣版，url 以 .html 結尾"""
  _my_host = {
    "name": "中時電子報",
    "url": "http://www.chinatimes.com/",
  }

  _my_feeds = [
    {"title": "焦點", "url": "http://rss.chinatimes.com/rss/focus-u.rss"},
    {"title": "政治", "url": "http://rss.chinatimes.com/rss/Politic-u.rss"},
  ]

  def parse_response(self, payload):
    content = payload['html'].cssselect('.content .articlebox')

    if content is None or len(content) == 0: return None
    content = content[0]

    payload['content'] = content
    return payload
