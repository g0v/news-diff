# -*- coding: utf-8 -*-
#
from lib import Ctlr_Base_RSS_2_0

class Ctlr(Ctlr_Base_RSS_2_0):
  _created_on = '2013-07-25T16:33:26Z'

  _my_feeds = [
    {"title": "全部文章", "url": "http://feeds.feedburner.com/coolloudheadlines?format=xml"},
  ]

  def parse_response(self, payload):
    hits = payload['html'].cssselect(
      '.article .post-header, .article .post-title, .article .post-author, ' \
      '.article .post-content, .article .post-meta-2'
    )

    if hits is None or len(hits) < 5: return None
    payload['content'] = hits
    return payload
