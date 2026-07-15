"""PowerShellTool - native PowerShell command execution."""
import asyncio
from src.tools.base import Tool

class PowerShellTool(Tool):
    name = "powershell"
    description = "Execute a PowerShell command on Windows"
    parameters_schema = {"type":"object","properties":{"command":{"type":"string","description":"PowerShell command"},"timeout":{"type":"integer","default":30}},"required":["command"]}

    def __init__(self):
        self.workdir = None

    async def execute(self, command, timeout=30):
        cwd = self.workdir or "."
        try:
            proc = await asyncio.create_subprocess_exec("powershell.exe","-NoProfile","-Command",command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {"exit_code": proc.returncode, "stdout": stdout.decode("utf-8","replace"), "stderr": stderr.decode("utf-8","replace")}
        except asyncio.TimeoutError:
            proc.kill()
            return {"exit_code": -1, "stdout": "", "stderr": f"Command timed out after {timeout}s"}
