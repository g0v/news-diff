import urllib
from threading import *
import Queue

class Worker(Thread):
  cond = Condition()

  def __init__(self, pool, output):
    Thread.__init__(self)
    self.pool = pool
    self.output = output

  def hit_portal(self, proc):
    import re
    ptrn = re.compile("\.feedsportal\.com")

    if (ptrn.search(proc['url'])):
      # feedsportal, get real url
      from lxml.html import fromstring
      try:
        html = fromstring(proc['response'])
        proc['url'] = html.cssselect('a')[0].attrib['href']
      except Exception:
        print('** Portal error, proc :')
        print(proc)

      del proc['response']

      self.pool.put(proc)
      return True

    return False

  def run(self):
    self.say('started')
    while True:
      try:
        proc = self.pool.get(False, 1)
      except Queue.Empty:
        break

      try:
        self.say('fetching from %s' % proc['url'])
        uo = urllib.urlopen(proc['url'])
        response = uo.read()
        proc['url'] = uo.url
      except Exception as e:
        response = 'error ' + unicode(e)

      proc['response'] = response
      proc['status'] = "response"

      # begin lock
      self.cond.acquire()

      if (not self.hit_portal(proc)):
        self.output.append(proc)

      self.pool.task_done()
      self.cond.release()
      # end lock
      #
    self.say('terminated')

  def say(self, msg):
    return
    print('[%s]: %s' % (self.getName(), msg))

class Fetcher:
  """Fetche files from remote servers; fires callback if success"""
  def __init__(self):
    self._process_q = Queue.Queue(0)

  def queue(self, url, callback = None, category = None, meta = None):
    queue_body = {'url': url, 'cb': callback, 'category': category}

    if (meta):
      queue_body['meta'] = meta
    else:
      queue_body['meta'] = {}

    self._process_q.put(queue_body)

  def start(self):
    from . import db, conf

    output = []
    pool = self._process_q
    self._process_q = Queue.Queue(0)

    #init worker threads
    for i in xrange(min(conf['fetcher']['threads'], pool.qsize())):
      Worker(pool, output).start()

    pool.join()

    for proc in output:
      db.save_fetch(proc['url'], proc['response'], proc['category'])
      del proc['category'] # consumed here

      if (proc['cb']):
        proc['cb'](proc)
        proc['cb'] = unicode(proc['cb'])

    return output
