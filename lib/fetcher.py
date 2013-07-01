import urllib

class Fetcher:
  """Fetche files from remote servers; fires callback if success"""
  def __init__(self):
    self._process_q = []

  def register(self, url, callback = None):
    self._process_q.append({'url': url, 'cb': callback})

  def start(self):
    output = []

    for proc in self._process_q:
      try:
        content = urllib.urlopen(proc['url']).read()
        if (proc['cb']):
          proc['cb'](content)
          continue

        proc['content'] = content

      except IOError:
        proc['result'] = 'error'

      output.append(proc)

    self._process_q = []
    return output
