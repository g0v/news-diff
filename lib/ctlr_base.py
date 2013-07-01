# -*- encoding:utf-8 -*-

class Ctlr_base:
  """Controller base class
  Serves utility methods and function templates"""
  name = "Default Ctlr"
  _date_online = 0
  _date_expire = None

  @staticmethod
  def to_date(value, fmts = None):
    from datetime import datetime

    if type(value) is int:
      # interpret as timestamp
      return datetime(value)

    if type(value) is datetime:
      return value

    if (fmts is None):
      fmts = [
        '%Y'
      ]

    for fmt in fmts:
      try:
        dt = datetime.strptime(value, fmt)
        return dt
      except ValueError:
        continue

    # no format found
    raise ValueError('Can\'t parse date ' + value)

  @staticmethod
  def to_timestamp(value, fmts = None):
    import time
    return time.mktime(Ctlr_base.to_date(value, fmts).utctimetuple())

  def __init__(self):
    # date values
    pass

  def parse_article(self, payload):
    """處理針對單則新聞的 callback"""
    del(payload['content'])
    print(payload)

  def run(self):
    """Implement Program Logic Here"""
    print(self)
    print('running')
    pass

