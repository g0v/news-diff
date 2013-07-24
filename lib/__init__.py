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
from net import fetch
from db import DB
from ctlr_base import Ctlr_Base
from ctlr_base_rss_2_0 import Ctlr_Base_RSS_2_0
from proc import Queue

# logging
_format = '%(classname)-35s %(levelname)s %(message)s'
logging.basicConfig(format=_format)
logger = logging.getLogger('news-diff')
logger.setLevel(logging.WARNING)

# Util
def md5(unicode_str):
  from hashlib import md5
  return md5(unicode_str).hexdigest()
