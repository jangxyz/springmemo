#!/usr/bin/python

import subprocess
import sys, os, time
from datetime import datetime

if len(sys.argv) < 3:
   sys.exit('Usage: %s target_filename test_file [command]' % sys.argv[0])

target  = os.path.abspath(sys.argv[1])
test    = sys.argv[2]
command = sys.argv[3].split() if len(sys.argv) >= 4 else ['python', test]

def recent_modified_time(filenames):
    return max([os.stat(file).st_mtime for file in filenames])

def run_command(cmd):
    #os.popen('python %s' % test)
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    print "[ %s ]" % datetime.now()
    print result


last_changed_time = recent_modified_time([target, test])
while True:
    new_changed_time = recent_modified_time([target, test])
    if last_changed_time != new_changed_time:
        run_command(cmd)
        last_changed_time = new_changed_time
    #
    time.sleep(1)


