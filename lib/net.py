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

def fix_portal_url(portal, url):
  try:
    if 'feedsportal' == portal:
      return _fix_portal_url_feedsportal(url)
  except Exception:
    print('*** Fix Portal Failed (%s, %s) ***' % (portal, url))

  raise "can't fix"

def _fix_portal_url_feedsportal(url):
  from lxml.html import fromstring
  html = fromstring(urllib.urlopen(url).read())
  return html.cssselect('a')[0].attrib['href']

def fetch(payload):
  from . import DB
  db = DB()

  # feed portal services like feedsportal.com
  portal = get_portal(payload['url'])
  if portal:
    payload['url'] = fix_portal_url(portal, payload['url'])

  try:
    uo = urllib.urlopen(payload['url'])
    response = uo.read()
    payload['url_read'] = uo.url
  except Exception as e:
    response = 'error ' + unicode(e)
    payload['category'] = 'error'

  payload['response'] = response

  db.save_fetch(payload['url'], payload['response'], payload['category'])
  del payload['category'] # consumed here

  return payload
