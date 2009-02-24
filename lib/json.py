"""
  a proxy json module
  that calls simplejson with default parameter encode_datetime, which encodes datetime in specific format
"""

import simplejson
from datetime import datetime

def encode_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y/%m/%d %H:%M:%S +0000")
    raise TypeError(repr(obj) + " is not JSON serializable")

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        encoding='utf-8', default=None, **kw):
    return simplejson.dumps(obj, skipkeys, ensure_ascii, check_circular, allow_nan, cls, indent, separators, encoding, encode_datetime, **kw)

loads=simplejson.loads

