# -*- coding: utf-8 -*-
#
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  """文字為主，包含 float:left 重點圖的頁面；可用 $('.news_content') 辨識"""

  _created_on = '2013-08-14T15:55:00Z'
  _my_feeds = [
    {"title": "重點", "url": "http://feeds.feedburner.com/cnaFirstNews?format=xml"},
    {"title": "政治", "url": "http://feeds.feedburner.com/rsscna/politics?format=xml"},
    {"title": "財經", "url": "http://feeds.feedburner.com/rsscna/finance?format=xml"},
    {"title": "國際", "url": "http://feeds.feedburner.com/rsscna/intworld?format=xml"},
    {"title": "兩岸", "url": "http://feeds.feedburner.com/rsscna/mainland?format=xml"},
    {"title": "文教", "url": "http://feeds.feedburner.com/rsscna/education?format=xml"},
    {"title": "科技", "url": "http://feeds.feedburner.com/rsscna/technology?format=xml"},
    {"title": "生活", "url": "http://feeds.feedburner.com/rsscna/lifehealth?format=xml"},
    {"title": "體育", "url": "http://feeds.feedburner.com/rsscna/sportstars?format=xml"},
    {"title": "社會", "url": "http://feeds.feedburner.com/rsscna/social?format=xml"},
  ]

  def parse_response(self, payload):
    sel_list = [
      '.news_content > h1',
      '.news_content .date',
      '.news_content .box_0',
    ]

    hits = payload['html'].cssselect(", ".join(sel_list))
    if len(hits) != len(sel_list): return False

    opt_list = ['.news_content .latest_news_key']
    opt = payload['html'].cssselect(", ".join(opt_list))
    if len(opt) > 0: hits = hits + opt

    payload['content'] = hits
    return payload

class Ctlr_Photo(Ctlr_Base_RSS_2_0):
  """中左組圖，右邊說明文字頁面"""

  _created_on = '2013-08-14T15:55:00Z'
  _my_feeds = [
    {"title": "鏡頭看世界", "url": "http://feeds.feedburner.com/rsscna/PhotoAlbum?format=xml"},
  ]

  def parse_response(self, payload):
    sel_list = [
      '.photo_content > h1',
      '.photo_content .box_0',
    ]

    hits = payload['html'].cssselect(", ".join(sel_list))
    if len(hits) != len(sel_list): return False

    payload['content'] = hits
    return payload
