#!/usr/bin/python

import sys, time, os

if len(sys.argv) != 3:
	sys.exit('Usage: %s target_file test_file' % sys.argv[0])
   

target_file = sys.argv[1]
test_file   = sys.argv[2]

def recent_changed_time(file):
	return os.stat(file).st_mtime

start_time = recent_changed_time(target_file)
print start_time

while True:
	new_time = max(recent_changed_time(target_file), recent_changed_time(test_file))
	if new_time != start_time:
		print new_time
		start_time = new_time
		os.popen('python %s' % test_file)
	time.sleep(1)

