# define feeds srouces

def _feed_dict(feed_url, source, handler, catalog=None):
    return dict(feed_url=feed_url,
                source=source,
                handler=handler,
                catalog=catalog,
                last=None)

default_feeds = []
default_feeds.append(_feed_dict('http://www.libertytimes.com.tw/rss/fo.xml', u'自由時報', 'libertytimes', u'焦點'))
default_feeds.append(_feed_dict('http://www.libertytimes.com.tw/rss/p.xml', u'自由時報', 'libertytimes', u'政治'))
default_feeds.append(_feed_dict('http://www.libertytimes.com.tw/rss/e.xml', u'自由時報', 'libertytimes', u'財經'))
default_feeds.append(_feed_dict('http://rss.chinatimes.com/rss/focusing-u.rss', u'中時電子報', 'chinatimes', u'首頁焦點'))
default_feeds.append(_feed_dict('http://rss.chinatimes.com/rss/focus-u.rss', u'中時電子報', 'chinatimes', u'焦點'))
default_feeds.append(_feed_dict('http://rss.chinatimes.com/rss/Politic-u.rss', u'中時電子報', 'chinatimes', u'政治'))
#default_feeds.append(_feed_dict('http://rss.chinatimes.com/rss/finance-u.rss', u'中時電子報', 'chinatimes', u'財經'))
default_feeds.append(_feed_dict('http://www.appledaily.com.tw/rss/create/kind/sec/type/1077', u'蘋果日報', 'appledaily', u'頭條'))
default_feeds.append(_feed_dict('http://www.appledaily.com.tw/rss/create/kind/sec/type/151', u'蘋果日報', 'appledaily', u'政治'))
default_feeds.append(_feed_dict('http://www.appledaily.com.tw/rss/create/kind/sec/type/11', u'蘋果日報', 'appledaily', u'要聞'))

