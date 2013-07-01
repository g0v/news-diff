class Ctlr_base:
  """Controller base class
  Serves utility methods and function templates"""
  name = "Default Ctlr"
  _date_online = 0
  _date_expire = None

  @staticmethod
  def to_date(value):
    return 3

  def __init__(self):
    # date values
    pass

  def run(self):
    """Implement Program Logic Here"""
    print(self)
    print('running')
    pass
