# Config
import json
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

# Util
def say(msg, self = None):
  hdr = ""
  if not self is None:
    hdr = "[%s]\t" % unicode(self)

  print("%s%s" % (hdr, msg))

def md5(unicode_str):
  from hashlib import md5
  return md5(unicode_str).hexdigest()
