# -*- encoding: utf-8 -*-
#
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _created_on = '2013-07-30T23:30:00 UTC'

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
    from lxml.html import fromstring, tostring
    sel_list = [
        '#content .news_ctxt_area_rt1 .news_ctxt_area_pic',
        '#content .news_ctxt_area_rt1 .news_ctxt_area_word_13pt',
    ]
    _hits = payload['html'].cssselect(", ".join(sel_list))

    if len(_hits) not in (0,2): return False

    sel_list = [
        '#content .news_cont_area_tit',
        '#content .news_ctxt_area_lt1 .news_ctxt_area_word',
    ]
    hits = payload['html'].cssselect(", ".join(sel_list))

    if hits is None or len(hits) != len(sel_list): return False
    hits[1:1] = _hits

    payload['content'] = fromstring('\n'.join([tostring(x, encoding=unicode) for x in hits]))
    return payload
