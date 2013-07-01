from bs4 import BeautifulSoup
import urllib2
import re
import rss_base

class Handler(rss_base.RssBaseHandler):
    # parser id
    id = 2

    def fetch_text(self, link):
        return fetch_text(link)

def fetch_text(url):
    try:
        u = urllib2.urlopen(url)
        url = u.geturl()
        bs = BeautifulSoup(u)
        if 'iservice' in url:
            fetched = bs.find(attrs={'id': re.compile('newsc'),
                                     'role': re.compile('article')}).get_text()
        else:
            fetched = bs.find(attrs={'id': re.compile('newsContent')})
                            .find_all('span')[1].get_text()
        return url, fetched
    except Exception, e:
        #raise
        return url, None
