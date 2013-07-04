# Config
import json
from os.path import dirname, join

_filenames = ['db', 'timings']
conf = {}

for _filename in _filenames:
  with open(join(dirname(dirname(__file__)), 'conf', _filename + '.json'), 'r') as fp:
    conf[_filename] = json.load(fp)

# Class aliases
import fetcher, ctlr_base, ctlr_base_rss, db

Fetcher = fetcher.Fetcher
Ctlr_Base = ctlr_base.Ctlr_Base
Ctlr_Base_RSS = ctlr_base_rss.Ctlr_Base_RSS

db = db.DB.forge()
