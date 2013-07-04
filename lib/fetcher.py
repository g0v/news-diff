import urllib

class Fetcher:
  """Fetche files from remote servers; fires callback if success"""
  def __init__(self):
    self._process_q = []

  def queue(self, url, callback = None, category = None, meta = None):
    queue_body = {'url': url, 'cb': callback, 'category': category}

    if (meta):
      queue_body['meta'] = meta
    else:
      queue_body['meta'] = {}

    self._process_q.append(queue_body)

  def start(self):
    from . import db

    output = []

    for proc in self._process_q:
      try:
        response = urllib.urlopen(proc['url']).read()
        proc['response'] = response

        db.save_fetch(proc['url'], proc['response'], proc['category'])
        del proc['category'] # consumed here

        if (proc['cb']):
          cb = proc['cb']
          del(proc['cb'])
          cb(proc)
          continue

      except IOError:
        proc['result'] = 'error'

      output.append(proc)

    self._process_q = []
    return output
