"""BashTool - execute shell commands via subprocess."""
import asyncio, os, platform
from src.tools.base import Tool

class BashTool(Tool):
    name = "bash"
    description = "Execute a shell command in the project directory"
    parameters_schema = {"type":"object","properties":{"command":{"type":"string","description":"The shell command to execute"},"timeout":{"type":"integer","description":"Timeout in seconds","default":30}},"required":["command"]}

    def __init__(self, workdir=None):
        self.workdir = workdir or os.getcwd()

    async def execute(self, command, timeout=30):
        try:
            shell_cmd = "powershell.exe" if platform.system() == "Windows" else "/bin/bash"
            proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=self.workdir, executable=shell_cmd)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {"exit_code": proc.returncode, "stdout": stdout.decode("utf-8","replace"), "stderr": stderr.decode("utf-8","replace"), "cwd": self.workdir}
        except asyncio.TimeoutError:
            proc.kill()
            return {"exit_code": -1, "stdout": "", "stderr": f"Command timed out after {timeout}s", "cwd": self.workdir}
