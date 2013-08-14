# -*- encoding: utf-8 -*-
#

import urllib

portal_ptrn_list = {
  'feedsportal': "\.feedsportal\.com",
}

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

  text = uo.read()
  try:
    html = fromstring(text)
    payload['url_read'] = html.cssselect('a')[0].attrib['href']
    payload['src'] = urllib.urlopen(payload['url_read'])
  except:
    payload['url_read'] = uo.url
    payload['src'] = text

def fetch(payload, dbi = None):
  """抓取 payload['url'] 的檔案
  並將最終讀取到的 url 寫入 payload['url_read'], response 寫入 payload['src']
  """
  import re
  from lxml.html import fromstring

  from lib import db, DB
  from lib.util.text import to_unicode

  try:
    uo = urllib.urlopen(payload['url'])
    portal = get_portal(uo.url)
    if portal:
      break_portal(portal, payload, uo)
    else:
      payload['src'] = uo.read()
      payload['url_read'] = uo.url

  except Exception as e:
    payload['src'] = 'error ' + unicode(e)
    payload['category'] = 'error'
    payload['exception'] = e


  if 'url_read' not in payload:
    payload['url_read'] = payload['url']

  if dbi is None: _dbi = DB()
  else: _dbi = dbi

  db.save_fetch(payload['url'], to_unicode(payload['src']), payload['category'], dbi = _dbi)
  if dbi is None: _dbi.disconnect()

  if 'error' == payload['category']:
    logger.warning("failed fetching %s", payload['url'],  extra={'classname':self.__class__})
    raise payload['exception']

  return payload

def normalize_url(url):
  import re
  url = url.rstrip('/')
  return re.sub('^https?://', '', url)
