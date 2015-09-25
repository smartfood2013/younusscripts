#!/usr/bin/env python3

import sys, os, string, time, signal, errno

class daemon:
    def __init__(self, name, logdir):
        self.name = name
        self.logdir = logdir
        self.DAEMON_RUNNING = "DAEMON_RUNNING"
        self.DAEMON_NOT_RUNNING = "DAEMON_NOT_RUNNING"
        self.DAEMON_STOPPED = "DAEMON_STOPPED"
        self.DAEMON_PID_FILE_DOES_NOT_EXIST = "DAEMON_PID_FILE_DOES_NOT_EXIST"
        self.USAGE = "Usage:" + self.name + " [stop|status|restart]\n"
        # Check, if the log directory is already there. If not, create it
        if not os.path.isdir(self.logdir):
            os.mkdir(self.logdir, 0o755)

    def cleanup(self):
        pass
    
    # Terminate daemon
    def _terminate(self, signal, param):
        try:
            # Do necessary cleanup handling
            self.cleanup()
            # Remove the pid file
            os.remove(os.path.join(self.logdir, 'run.pid'))
        except:
            pass
        sys.stdout.write("..........terminating\n")
        sys.exit(0)

    def _daemonize(self):
        self.printStartupMsg()        
        # Change to the log directory
        os.chdir(self.logdir)
        self._setupIfNotStartedByInitProcess()
        self._detachTerminal()
        # Reset the umask
        os.umask(000)
        self.initSignalHandling()
        self._savepid()
    
    def _start(self):
        # Start Daemon
        if self._isDaemonRunning():
            sys.stderr.write(self.name + ":" + self.DAEMON_RUNNING)
            sys.exit(0)
        self._daemonize()
        self.run()

    def _stop(self):
        # Stop Daemon
        if self._isDaemonRunning():
            pid = self._getdaemonpid()
            os.kill(pid, signal.SIGTERM)
            sys.stdout.write(self.name + ":" + self.DAEMON_STOPPED)
            sys.exit(0)
        sys.stdout.write(self.name + ":" + self.DAEMON_NOT_RUNNING)
        sys.exit(1)

    def _status(self):
        # Daemon Status
        if self._isDaemonRunning():
            sys.stdout.write(self.name + ":" + self.DAEMON_RUNNING)
        else:
            sys.stdout.write(self.name + ":" + self.DAEMON_NOT_RUNNING)
        sys.exit(0)

    def _restart(self):
        # Restart Daemon
        self._stop()
        self._start()

    def startDaemon(self):
        name = self.name
        # Get the call arguments (stop, status, restart)
        if len(sys.argv) > 2:
            sys.stderr.write(self.USAGE)
            sys.exit(1)
        if len(sys.argv) == 2:
            if sys.argv[1] == 'stop':
                self._stop()        
            elif sys.argv[1] == 'status':
                self._status()
            elif sys.argv[1] == 'restart':
                self._restart()
            else:
                sys.stderr.write(self.USAGE)
                sys.exit(1)
        self._start()

    def _getdaemonpid(self):
        if os.path.isfile(os.path.join(self.logdir, 'run.pid')):
            f = open(os.path.join(self.logdir, 'run.pid'), 'r')
            pid = int(f.readline().strip())
            f.close()
            return pid
        raise (OSError(self.DAEMON_PID_FILE_DOES_NOT_EXIST))
        
    def _isDaemonRunning(self):
        logdir = self.logdir
        # Check, if there is already a running instance
        if os.path.isfile(os.path.join(logdir, 'run.pid')):
            pid = self._getdaemonpid()
            try:
                os.kill(pid, 0)
            except OSError as e:
                if e.errno != errno.ESRCH: # NO SUCH PROCESS
                     raise (OSError(e.args[0]))
            else:
                return True
        return False

    def _setupIfNotStartedByInitProcess(self):
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

    def _detachTerminal(self):
        # Initialize error logging
        f_stderr = open(os.path.join(self.logdir, 'error.log'), 'w')
            
        # Initialize message logging
        f_stdout = open(os.path.join(self.logdir, 'message.log'), 'w')

        # Close sys.stdin
        sys.stdin.close()
        # Close sys.stdout and redirect the message log to sys.stdout
        sys.stdout.close()
        sys.stdout = f_stdout
        # Close sys.stderr and redirect the error log to sys.stderr
        sys.stderr.close()
        sys.stderr = f_stderr

    def initSignalHandling(self):
        def term(signal, param):
            self._terminate(signal, param)
        # Ignore a dead of child signal
        signal.signal(signal.SIGCLD, signal.SIG_IGN)
        # Install a hander for ther terminate signal
        signal.signal(signal.SIGTERM, term)
        # Install a handler for the interrupt signal
        signal.signal(signal.SIGINT, term)
        # Install a handler for the quit signal
        signal.signal(signal.SIGQUIT, term)

    def _savepid(self):
        # Write our process id into the pid file
        f = open(os.path.join(self.logdir, 'run.pid'), 'w')
        f.write("%d" % os.getpid())
        f.close()

    def printStartupMsg(self):
        # Print a startup message
        ctime = time.strftime("%d.%m.%Y / %H:%M:%S", time.localtime(time.time()))
        sys.stdout.write("{}: started at {}\n".format(self.name, ctime))
        sys.stdout.write("{a}: log directory is '{b}' \n".format(a=self.name, b=self.logdir))
        sys.stdout.write("{}: going into background........\n".format(self.name))
        sys.stdout.flush()
