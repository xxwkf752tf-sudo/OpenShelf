"""ErrorAnalyzer - intelligent shell error analysis."""
import re

class ErrorAnalyzer:
    ERROR_PATTERNS = [
        (r"ModuleNotFoundError: No module named '(.*)'", "Run: pip install {group1}"),
        (r"ImportError: cannot import name '(.*)'", "Check if the module is installed and the import name matches"),
        (r"SyntaxError: (.*)", "Syntax error: {group1}"),
        (r"PermissionError: (.*)", "Permission denied: {group1}. Try running as administrator"),
        (r"FileNotFoundError: (.*)", "File not found: {group1}"),
        (r"command not found: (.*)", "Command not found: {group1}. Check PATH or install the tool"),
    ]

    @classmethod
    def analyze(cls, stderr_output):
        suggestions = []
        for pattern, suggestion in cls.ERROR_PATTERNS:
            match = re.search(pattern, stderr_output)
            if match:
                msg = suggestion
                for i, group in enumerate(match.groups(), 1):
                    msg = msg.replace(f"{{group{i}}}", group)
                suggestions.append(msg)
                if len(suggestions) >= 3:
                    break
        return {"errors_found": len(suggestions) > 0, "suggestions": suggestions}
