# -*- encoding: utf-8 -*-
#
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _created_on = '2013-07-25T16:33:26'

  _my_feeds = [
    {"title": "要聞", "url": "http://newtalk.tw/rss_news.php"},
    {"title": "國際", "url": "http://newtalk.tw/rss_news.php?oid=1"},
    {"title": "政治", "url": "http://newtalk.tw/rss_news.php?oid=2"},
    {"title": "財金", "url": "http://newtalk.tw/rss_news.php?oid=3"},
    {"title": "司法", "url": "http://newtalk.tw/rss_news.php?oid=4"},
    {"title": "生活", "url": "http://newtalk.tw/rss_news.php?oid=5"},
    {"title": "媒體", "url": "http://newtalk.tw/rss_news.php?oid=6"},
    {"title": "中國", "url": "http://newtalk.tw/rss_news.php?oid=7"},
    {"title": "科技", "url": "http://newtalk.tw/rss_news.php?oid=8"},
    {"title": "環保", "url": "http://newtalk.tw/rss_news.php?oid=9"},
    {"title": "地方", "url": "http://newtalk.tw/rss_news.php?oid=14"},
  ]

  def parse_response(self, payload):
    content = payload['html'].cssselect('#content')

    if content is None or len(content) == 0: return None
    content = content[0]

    self.css_sel_drop_tree(content, [
        '.cont_green_tit', '.cgt_bg_1', '.news_cont_area_top',
        '.news_cont_area_tit_space', '.news_cont_talker_write',
        '#_relay_reply', "#fb-root", '.fb_comments'
      ])

    payload['content'] = content
    return payload
