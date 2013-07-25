# -*- encoding:utf-8 -*-
#
#

import logging

_format = '%(classname)-35s %(levelname)s %(message)s'
logging.basicConfig(format=_format)

logger = logging.getLogger('news-diff')
logger.setLevel(logging.WARNING)
