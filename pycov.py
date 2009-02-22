#!/usr/bin/python

import subprocess
import sys, os, time

if len(sys.argv) < 3:
   print 'Usage: %s target_filename test_file' % sys.argv[0]
   sys.exit()

filename = os.path.abspath(sys.argv[1])
test = sys.argv[2]

def get_mtime(filename):
   return os.stat(filename).st_mtime

last_changed_time = max(get_mtime(filename), get_mtime(test))
while True:
   new_changed_time = max(get_mtime(filename), get_mtime(test))
   if last_changed_time != new_changed_time:
#        os.popen('python %s' % test)
       result = subprocess.Popen(['python',test], stdout=subprocess.PIPE).communicate()[0]
       print result
       last_changed_time = new_changed_time
   time.sleep(1)
