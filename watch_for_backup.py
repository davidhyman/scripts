import sys  
import hashlib
import shutil
import os
import time

# hacky script for backing up a file
# file, output dir, checking interval

args = sys.argv

target = args[1]

target_filename =  os.path.split(target)[1]

output = args[2]

output_format = "%s.%s"

interval = int(args[3]) if len(args) > 3 else 1

def get_hash():
    hasher = hashlib.sha1()
    with open(target, 'rb') as fh:
        hasher.update(fh.read())
    return hasher.hexdigest()
    
def backup():
    dest = os.path.join(output, output_format % (int(time.time()), target_filename))
    shutil.copyfile(target, dest)
    print 'backup: %s %s' % (time.strftime('%H:%M:%S'), dest)

if not os.path.exists(target):
    print 'file does not exist yet, waiting ...'
while not os.path.exists(target):
    time.sleep(interval)
    
h_old = None
t_old = None
while True:
    # check timestamps (cheap)
    t_new = os.path.getmtime(target)
    if t_new != t_old:
        t_old = t_new
                
        # check hash (less cheap)
        h_new = get_hash()
        if h_new != h_old:
            backup()
            h_old = h_new
        else:
            print 'timestamp change, no backup: %s' % t_new
            
    time.sleep(interval)