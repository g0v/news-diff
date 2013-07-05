#usr/bin/python
#-*- encoding:utf-8 -*-

import lib
import proc from lib
import importlib

# Fetch RSS
ctlr_pkg_list = [
  'appledaily'
]

if False:
  for pkg in ctlr_pkg_list:
    ns_tmp = importlib.import_module('lib.%s' % pkg)

    for ctlr in ns_tmp.Ctlrs:
      ctlr().run()

# Revisits


lib.db.disconnect()
