# -*- coding:utf-8 -*-
#
#

import json
from os.path import dirname, join

_filenames = ['db', 'config']
conf = {}

for _filename in _filenames:
  with open(join(dirname(dirname(__file__)), 'conf', _filename + '.json'), 'r') as fp:
    conf[_filename] = json.load(fp)
