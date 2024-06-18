import sys  
import hashlib
import shutil
import os
import time

from pathlib import Path

# hacky script for backing up a file;
# provide commandline args as:
# file, output dir, [checking interval in ms, 500]

# n.b. should use inode watchers rather than polling ...

args = sys.argv

target = Path(args[1])

target_filename = target.name

output = Path(args[2])

interval_ms = int(args[3]) if len(args) > 3 else 500
interval = interval_ms / 1000

print(f"will backup {target} to {output/target_filename} every {interval} seconds")


def get_hash():
    hasher = hashlib.sha1()
    content = target.read_bytes()
    hasher.update(content)
    return hasher.hexdigest()


def backup():
    dest = output / f"{int(time.time())}.{target_filename}"
    shutil.copyfile(target, dest)
    print('backup: %s %s' % (time.strftime('%H:%M:%S'), dest))


_state = None
h_old = None
t_old = None
while True:
    try:
        # check timestamps (cheap)
        t_new = os.path.getmtime(target)
        _state = True
        if t_new != t_old:
            t_old = t_new

            # check hash (less cheap)
            h_new = get_hash()
            if h_new != h_old:
                backup()
                h_old = h_new
            else:
                print('timestamp change, no backup: %s' % t_new)

    except FileNotFoundError:
        if _state is not False: print('file does not exist yet, waiting ...')
        _state = False

    time.sleep(interval)
