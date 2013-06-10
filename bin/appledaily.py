from bs4 import BeautifulSoup
import urllib2
import re
from datetime import datetime
import rss_base
# Sat, 01 Dec 2012 07:00:00 +0800
process_date = lambda x: x[5:-6]
DATE_FORMAT =  '%d %b %Y %H:%M:%S'

class Handler(rss_base.RssBaseHandler):
    # parser id
    id = 1

    def fetch_text(self, link):
        return fetch_text(link)

    def _str_to_ts(self, pubdate_str):
        ts = datetime.strptime(process_date(pubdate_str), DATE_FORMAT)
        ts = ts.replace(tzinfo=rss_base.UTC8())
        return ts.astimezone(rss_base.UTC())

def fetch_text(url):
    try:
        u = urllib2.urlopen(url)
        url = u.geturl()
        bs = BeautifulSoup(u)
        return url, bs.find(attrs={'class': re.compile('articulum')}).get_text()
    except Exception, e:
        #raise
        return url, None
