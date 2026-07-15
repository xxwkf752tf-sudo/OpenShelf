"""ProcessManager - subprocess lifecycle management."""
import subprocess, asyncio, platform

class ProcessManager:
    @staticmethod
    async def run(command, cwd=None, timeout=30, env=None):
        shell = platform.system() == "Windows"
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd, env=env) if shell else await asyncio.create_subprocess_exec(*command.split(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd, env=env)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {"returncode": proc.returncode, "stdout": stdout.decode("utf-8","replace"), "stderr": stderr.decode("utf-8","replace")}
        except asyncio.TimeoutError:
            proc.kill()
            return {"returncode": -1, "stdout": "", "stderr": "Timeout"}

    @staticmethod
    def run_sync(command, cwd=None, timeout=30):
        try:
            result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
            return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stdout": "", "stderr": "Timeout"}
