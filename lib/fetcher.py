import urllib

class Fetcher:
  """Fetche files from remote servers; fires callback if success"""
  def __init__(self):
    self._process_q = []

  def queue(self, url, callback = None, **meta):
    self._process_q.append({'url': url, 'cb': callback, 'meta': meta})

  def start(self):
    output = []

    for proc in self._process_q:
      try:
        content = urllib.urlopen(proc['url']).read()
        proc['content'] = content

        if (proc['cb']):
          proc['cb'](proc)
          continue

      except IOError:
        proc['result'] = 'error'

      output.append(proc)

    self._process_q = []
    return output
