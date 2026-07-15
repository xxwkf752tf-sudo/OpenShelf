"""TerminalSession - pty-driven single terminal."""
import subprocess, os, platform

class TerminalSession:
    def __init__(self, shell=None):
        if shell is None:
            shell = ["powershell.exe"] if platform.system() == "Windows" else ["/bin/bash"]
        self.shell = shell
        self._process = None
        self._output = []

    def start(self, cwd=None):
        cwd = cwd or os.getcwd()
        self._process = subprocess.Popen(self.shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, text=True, bufsize=1)

    def send(self, command):
        if self._process and self._process.stdin:
            self._process.stdin.write(command + "\n")
            self._process.stdin.flush()

    def read_line(self):
        if self._process and self._process.stdout:
            return self._process.stdout.readline()
        return ""

    def send_signal(self, sig):
        if self._process:
            self._process.send_signal(sig)

    def is_alive(self):
        return self._process is not None and self._process.poll() is None

    def terminate(self):
        if self._process:
            self._process.terminate()
            self._process = None
