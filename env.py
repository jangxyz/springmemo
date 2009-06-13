import sys, os

PROGNAME = "springmemo"

# check wxPython
try:
    import wx
except ImportError:
    sys.exit("""
    You need wxPython to run %s.
    visit http://www.wxpython.org/ to install it.
    """ % PROGNAME.title())

# constants
HOMEDIR  = os.path.dirname(os.path.abspath(__file__))
LIBDIR   = os.path.join(HOMEDIR, "lib")

ICON_DIR = os.path.join(HOMEDIR, "views", "images", "icons")

