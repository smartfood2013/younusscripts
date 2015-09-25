#!/usr/bin/env python3

from daemon import daemon
import os, time

LOG_DIR="/tmp/clipcopy"
class mydaemon(daemon):
    def run(self):
        archiver = clipboard_archiver()
        while True:
            archiver.add()
            # Replace the following sleep() by a real worker
            time.sleep(10)

def main():
    mydaemon1 = mydaemon("clipcopy", LOG_DIR)
    mydaemon1.startDaemon()
    
#
# Clipboard Archiver 
#
import pyperclip

class clipboard_archiver:
    def __init__(self):
        self.archiveFile = open(os.path.join(LOG_DIR, 'clip_archive.txt'), 'w')
        self.currenttxt = ''
    def add(self):
        newtxt = pyperclip.paste()
        if not self.currenttxt == newtxt:
            self.archiveFile.write(newtxt + '\n')
            self.archiveFile.flush()
            self.currenttxt = newtxt
    def close(self):
        self.archiveFile.close()

if __name__ == "__main__":
    main()
            
