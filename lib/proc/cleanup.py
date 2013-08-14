# -*- coding: utf-8 -*-

def cleanup(dbi = None):
  from lib import DB

  if dbi is None: _dbi = DB()
  else: _dbi = dbi

  _article(_dbi)
  _ctlr_feed(_dbi)

  if dbi is None: _dbi.disconnect()

def _article(dbi):
  """Remove dead rows from article sub-tables"""
  sql = "DELETE from `article__urls` where `hash` NOT IN ( " \
      "select `url_hash` from `articles` union "\
      "select `url_read_hash` from `articles` union "\
      "select `url_canonical_hash` from `articles` "\
  ")"

  dbi.execute(sql)

  pairs = {
    'text_hash': 'article__texts',
    'html_hash': 'article__htmls',
    'meta_hash': 'article__meta',
    'src_hash': 'article__srcs',
  }

  sql = "DELETE from `%s` where `hash` NOT IN (select `%s` from articles)"
  for x in pairs:
    dbi.execute(sql % (pairs[x], x))

def _ctlr_feed(dbi):
  sql = "DELETE FROM `ctlr_feed` WHERE (" \
    "`ctlr_id` NOT IN (SELECT `ctlr_id` FROM `ctlrs`) OR " \
    "`feed_id` NOT IN (SELECT `feed_id` FROM `feeds`)" \
  ")"
  dbi.execute(sql)
