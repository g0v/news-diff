from xml.dom import minidom
import urllib2
from datetime import datetime, tzinfo, timedelta
import email.utils

DATE_FORMAT =  '%d %b %Y %H:%M:%S'

class UTC(tzinfo):
    def utcoffset(self, dt): return timedelta(0)
    def dst(self, dt): return timedelta(0)

class UTC8(tzinfo):
    def utcoffset(self, dt): return timedelta(hours=8)
    def dst(self, dt): return timedelta(hours=8)

class RssBaseHandler(object):
    def get_articles(self, feed_url, last=None, limit=25):
        last = self._to_utc(datetime.strptime(last, DATE_FORMAT)) if last else datetime(1970, 1, 1, tzinfo=UTC())
        max_last = last
        articles = []
        f = urllib2.urlopen(feed_url)
        dom = minidom.parse(f)
        items = dom.getElementsByTagName('item')
        count = 0
        for item in items:
            if count > limit: break
            count += 1
            pubDate = self.getTextByTagName(item, 'pubDate')
            pubDate = self._str_to_ts(pubDate)
            if last and pubDate <= last:
                continue
            elif pubDate > max_last:
                max_last = pubDate
            link = self.getTextByTagName(item, 'link')
            title = self.getTextByTagName(item, 'title')
            link, cached = self.fetch_text(link)
            articles.append(dict(url=link,
                                 title=title,
                                 url_date=pubDate,
                                 cached=cached))
        return articles, max_last.strftime(DATE_FORMAT)

    def fetch_text(self, link):
        raise Exception('fetch_text not overwritten')

    def _str_to_ts(self, pubdate_str):
        # pubDate format: Wed, 28 Nov 2012 12:30:02 GMT
        return self._to_utc(datetime(*email.utils.parsedate(pubdate_str)[:6]))

    def _to_utc(self, date):
        return date.replace(tzinfo=UTC())

    def getTextByTagName(self, node, tagName):
        return self.getText(node.getElementsByTagName(tagName)[0])

    def getText(self, node):
        text = ''
        for child in node.childNodes:
            if child.nodeType in [child.TEXT_NODE, child.CDATA_SECTION_NODE]:
                text += child.data
        return text
