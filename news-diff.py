#usr/bin/python
#-*- encoding:utf-8 -*-

import lib
import importlib

host_list = [
  'appledaily'
]

for pkg in host_list:
  ns_tmp = importlib.import_module('lib.%s' % pkg)

  for ctlr in ns_tmp.Ctlrs:
    ctlr().run()

lib.db.disconnect()
