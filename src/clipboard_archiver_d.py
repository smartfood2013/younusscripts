#!/usr/bin/env python3

import sys, os, string, time, signal, errno
import pyperclip

LOG_DIR = '/tmp/clipboard_archiver'

#
# Signal Handlers
#
def terminate(signal, param):
    try:
        # Do necessary cleanup handling

        # Remove the pid file
        os.remove(os.path.join(LOG_DIR, 'run.pid'))
    except:
        pass
    sys.stdout.write("..........terminating\n")
    sys.exit(0)

#
# Main Routine
#
call_name = os.path.split(sys.argv[0])[1]

# Get the call arguments (stop, status)
if len(sys.argv) > 2:
    sys.stderr.write("Usage: %s [stop|status]\n" % call_name)
    sys.exit(1)
if len(sys.argv) == 2:
    if sys.argv[1] == 'stop':
        if os.path.isfile(os.path.join(LOG_DIR, 'run.pid')):
            f = open(os.path.join(LOG_DIR, 'run.pid'), 'r')
            pid = int(f.readline().strip())
            f.close()
            try:
                os.kill(pid, 0)
            except OSError as e:
                sys.stdout.write("Error:" + str(e) +  "\n")
                sys.stdout.write("ErrorNo:" + str(e.errno) +  "\n")
                if e.errno != errno.ESRCH: # NO SUCH PROCESS
                    raise (OSError(e.args[0]))
            else:
                os.kill(pid, signal.SIGTERM)
                sys.exit(0)            
        sys.stdout.write("%s: daemon is not running\n" % call_name)
        sys.exit(1)
    elif sys.argv[1] == 'status':
        if os.path.isfile(os.path.join(LOG_DIR, 'run.pid')):
            f = open(os.path.join(LOG_DIR, 'run.pid'), 'r')
            pid = int(f.readline().strip())
            f.close()
            try:
                os.kill(pid, 0)
            except OSError as e:
                if e.errno != errno.ESRCH: # NO SUCH PROCESS
                   raise (OSError(e.args[0]))
            else:
                sys.stdout.write("%s: daemon [%d] is running\n" % (call_name, pid))
                sys.exit(0)            
        sys.stdout.write("%s: daemon is not running\n" % call_name)
        sys.exit(0)
    else:
        sys.stderr.write("Usage: %s [stop|status]\n" % call_name)
        sys.exit(1)

# Check, if the log directory is already there. If not, create it
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR, 0o755)

# Check, if there is already a running instance
if os.path.isfile(os.path.join(LOG_DIR, 'run.pid')):
    f = open(os.path.join(LOG_DIR, 'run.pid'), 'r')
    pid = int(f.readline().strip())
    f.close()
    sys.stdout.write("pid: " + str(pid) + "\n")
    try:
        os.kill(pid, 0)
    except OSError as e:
        if e.errno != errno.ESRCH: # NO SUCH PROCESS
             raise (OSError(e.args[0]))
    else:
        sys.stderr.write("%s: there is already a running instance\n" % call_name)
        sys.exit(1)
        
# Initialize error logging
f_stderr = open(os.path.join(LOG_DIR, 'error.log'), 'w')
    
# Initialize message logging
f_stdout = open(os.path.join(LOG_DIR, 'message.log'), 'w')
    
# Print a startup message
sys.stdout.write("%s: started at %s\n" % (call_name, time.strftime("%d.%m.%Y / %H:%M:%S", time.localtime(time.time()))))
sys.stdout.write("%s: log directory is '%s'\n" % (call_name, LOG_DIR))
sys.stdout.write("%s: going into background........\n" % call_name)

# Initialize a daemon process
# Change to the log directory, this permits an umount on this directory
os.chdir(LOG_DIR)

# Do the following only, if we were not started by the init process
if os.getppid() != 1:
    # Ignore a terminal output signal
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    # Ignore a terminal input signal
    signal.signal(signal.SIGTTIN, signal.SIG_IGN)
    # Ignore a terminal stop signal
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    # Fork the first child
    pid = os.fork()
    # The parent ends here
    if pid > 0:
        sys.exit(0)
    # Make ourself a leader of the process group
    os.setpgrp()
    # Ignore a hangup signal
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    # Fork the second child
    pid = os.fork()
    # The parent ends here
    if pid > 0:
        sys.exit(0)

# Close sys.stdin
sys.stdin.close()
# Close sys.stdout and redirect the message log to sys.stdout
sys.stdout.close()
sys.stdout = f_stdout
# Close sys.stderr and redirect the error log to sys.stderr
sys.stderr.close()
sys.stderr = f_stderr
# Reset the umask
os.umask(000)
# Ignore a dead of child signal
signal.signal(signal.SIGCLD, signal.SIG_IGN)
# Install a hander for ther terminate signal
signal.signal(signal.SIGTERM, terminate)
# Install a handler for the interrupt signal
signal.signal(signal.SIGINT, terminate)
# Install a handler for the quit signal
signal.signal(signal.SIGQUIT, terminate)

# Write our process id into the pid file
f = open(os.path.join(LOG_DIR, 'run.pid'), 'w')
f.write("%d" % os.getpid())
f.close()

# Print a startup message
sys.stdout.write("%s: started at %s\n" % (call_name, time.strftime("%d.%m.%Y / %H:%M:%S", time.localtime(time.time()))))
sys.stdout.write("%s: log directory is is '%s'\n" % (call_name, LOG_DIR))
sys.stdout.write("%s: going into background........\n" % call_name)
sys.stdout.flush()

# Do other necessary initializations before entering the endless loop
#...
#...
#...

#============================================================================#
# Enter the endles loop                                                      #
#----------------------------------------------------------------------------#
def main():
    try: 
    
        archiver = clipboard_archiver()
        while(1):
            archiver.add()
            # Replace the following sleep() by a real worker
            time.sleep(10)
    except NameError as e:
        sys.stdout.write("Error:" + str(e)  +  "\n")
    

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
            
#============================================================================#
# EOF                                                                        #
#----------------------------------------------------------------------------#
