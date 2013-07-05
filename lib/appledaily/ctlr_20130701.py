# -*- encoding: utf-8 -*-
from .. import Ctlr_Base_RSS
from bs4 import BeautifulSoup

class Ctlr(Ctlr_Base_RSS):
  _my_host = {
    "name": "蘋果日報",
    "url": "http://www.appledaily.com.tw/",
  }

  _my_feeds = [
    {"title": "要聞", "url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/11"},
    #{"url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/151"},
    #{"url": "http://www.appledaily.com.tw/rss/create/kind/sec/type/1077"},
  ]

  def parse_article(self, payload):
    html = BeautifulSoup(payload['response'])
    wrapper = html.find(attrs={"class":"abdominis"})

    title = wrapper.find(attrs={"class": 'mpatc'}).header

    if (title and title.get_text()):
      payload['title'] = title.get_text()

    content = wrapper.find(attrs={"class": 'articulum'})

    payload['html'] = unicode(content)
    payload['text'] = content.get_text()

    return payload
