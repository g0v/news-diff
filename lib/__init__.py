# -*- encoding:utf-8 -*-
#
#

# Config
import json
import threading
import logging
from os.path import dirname, join

_filenames = ['db', 'config']
conf = {}

for _filename in _filenames:
  with open(join(dirname(dirname(__file__)), 'conf', _filename + '.json'), 'r') as fp:
    conf[_filename] = json.load(fp)

# Aliases
from db import DB
from ctlr import *
from util import Queue, Worker, fetch

import proc

# logging
_format = '%(classname)-35s %(levelname)s %(message)s'
logging.basicConfig(format=_format)
logger = logging.getLogger('news-diff')
logger.setLevel(logging.WARNING)
