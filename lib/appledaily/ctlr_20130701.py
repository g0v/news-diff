from .. import Ctlr_Base_RSS
from bs4 import BeautifulSoup

class Ctlr(Ctlr_Base_RSS):
  _rss_urls = [
    "http://www.appledaily.com.tw/rss/create/kind/sec/type/11",
    #"http://www.appledaily.com.tw/rss/create/kind/sec/type/151",
    #"http://www.appledaily.com.tw/rss/create/kind/sec/type/1077",
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
