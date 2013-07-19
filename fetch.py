#!/usr/bin/python
#-*- encoding:utf-8 -*-

import lib

# RSS-based Fetches
ctlr_list = [
  'appledaily',
  'chinatimes',
  'libertytimes',
]

lib.Ctlr_Base.do_fetch(ctlr_list)

# Revisits
lib.Ctlr_Base.do_revisit()

# Cleanup & Writeback
lib.db.disconnect()
