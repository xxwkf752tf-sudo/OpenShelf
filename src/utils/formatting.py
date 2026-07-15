"""Formatter - output formatting utilities."""
import json, textwrap

class Formatter:
    @staticmethod
    def pretty_json(obj):
        return json.dumps(obj, indent=2, ensure_ascii=False)

    @staticmethod
    def truncate(text, max_length=500):
        if len(text) <= max_length:
            return text
        return text[:max_length] + f"... [{len(text) - max_length} more chars]"

    @staticmethod
    def format_size(bytes_count):
        for unit in ["B","KB","MB","GB"]:
            if bytes_count < 1024:
                return f"{bytes_count:.1f}{unit}"
            bytes_count /= 1024
        return f"{bytes_count:.1f}TB"

    @staticmethod
    def format_duration(seconds):
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {secs:.1f}s"

    @staticmethod
    def wrap_text(text, width=100):
        return textwrap.fill(text, width=width)

    @staticmethod
    def strip_ansi(text):
        import re
        return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
