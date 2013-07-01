#usr/bin/python
#-*- encoding:utf-8 -*-

import lib
import importlib

ctlrs = [
  'appledaily'
]

for pkg in ctlrs:
  ns_tmp = importlib.import_module('lib.%s' % pkg)
  ctlr = ns_tmp.Ctlr()
  ctlr.run()


