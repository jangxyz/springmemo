import sys, os

# constants
PROGNAME = "springmemo"

HOMEDIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
LIBDIR   = os.path.join(HOMEDIR, "lib")
ICON_DIR = os.path.join(HOMEDIR, "views", "images", "icons")


# check wxPython
try:
    import wx
except ImportError:
    sys.exit("""
    You need wxPython to run %s.
    visit http://www.wxpython.org/ to install it.
    """ % PROGNAME.title())

