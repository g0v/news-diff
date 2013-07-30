# -*- encoding: utf-8 -*-
#
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _created_on = '2013-07-25T16:33:26 UTC'

  _my_feeds = [
    {"title": "國際焦點", "url": "http://udn.com/udnrss/international.xml"},
    {"title": "國內要聞", "url": "http://udn.com/udnrss/BREAKINGNEWS1.xml"},
    {"title": "最新報導", "url": "http://udn.com/udnrss/latest.xml"},
    {"title": "財經產業", "url": "http://udn.com/udnrss/BREAKINGNEWS6.xml"},
    {"title": "焦點要聞", "url": "http://udn.com/udnrss/focus.xml"},
    {"title": "政治要聞", "url": "http://udn.com/udnrss/politics.xml"},
    {"title": "社會新聞", "url": "http://udn.com/udnrss/social.xml"},
    {"title": "兩岸要聞", "url": "http://udn.com/udnrss/mainland.xml"},
    {"title": "國際財經", "url": "http://udn.com/udnrss/financeworld.xml"},
    {"title": "體壇動態", "url": "http://udn.com/udnrss/sportsfocus.xml"},
    {"title": "醫藥新聞", "url": "http://udn.com/udnrss/health.xml"},
  ]

  def parse_response(self, payload):
    from lxml.html import fromstring, tostring
    hits = payload['html'].cssselect('#story_title, #story_author, #story')

    if hits is None or len(hits) < 3: return None
    payload['content'] = fromstring('\n'.join([tostring(x, encoding=unicode) for x in hits]))
    return payload
