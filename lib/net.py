# -*- encoding: utf-8 -*-
#
portal_ptrn_list = {
  'feedsportal': "\.feedsportal\.com",
}

import urllib

def normalize_url(url):
  import re
  url = url.rstrip('/')
  return re.sub('^https?://', '', url)

def get_portal(url):
  import re

  for portal in portal_ptrn_list:
    ptrn = re.compile(portal_ptrn_list[portal])
    if (ptrn.search(url)): return portal

  return False

def break_portal(portal, payload, uo):
  try:
    if 'feedsportal' == portal:
      return _break_portal_feedsportal(payload, uo)
  except Exception:
    import traceback
    print('\n***\nBreak Portal Failed (%s, %s) ***' % (portal, payload['url']))
    traceback.print_exc()

def _break_portal_feedsportal(payload, uo):
  from lxml.html import fromstring

  html = fromstring(uo.read())
  payload['url_read'] = html.cssselect('a')[0].attrib['href']
  payload['response'] = urllib.urlopen(payload['url_read'])

def fetch(payload):
  import re
  from . import DB
  from lxml.html import fromstring
  db = DB()

  try:
    uo = urllib.urlopen(payload['url'])

    portal = get_portal(uo.url)
    if portal:
      break_portal(portal, payload, uo)
    else:
      payload['response'] = uo.read()
      payload['url_read'] = uo.url

    # encoding other than utf-8
    try:
      html = fromstring(payload['response'])
      tags = html.cssselect('meta[http-equiv=Content-Type]')
      if (len(tags) > 0 and re.search('charset\s*=\s*big5', tags[0].attrib['content'], re.I)):
        # 後續分析不依靠 meta tag，因此直接轉為 unicode
        payload['response'] = unicode(payload['response'], 'big5')
    except:
      # not html, do nothing
      pass

  except Exception as e:
    payload['response'] = 'error ' + unicode(e)
    payload['category'] = 'error'

  db.save_fetch(payload['url'], payload['response'], payload['category'])
  del payload['category'] # consumed here

  return payload
