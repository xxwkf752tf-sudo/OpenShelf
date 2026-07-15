"""MarkdownRenderer - convert markdown to HTML for Qt display."""
import re

class MarkdownRenderer:
    @staticmethod
    def to_html(text):
        html = text
        html = re.sub(r'</?think>', '', html)
        html = re.sub(r'```(w*)\n(.*?)\n```', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        html = re.sub(r'^### (.+)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'**(.+?)**', r'<strong>\1</strong>', html)
        html = re.sub(r'*(.+?)*', r'<em>\1</em>', html)
        html = re.sub(r'^- (.+)', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'\n\n', r'<br><br>', html)
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        html = f'<div style="font-family: Consolas, monospace; line-height: 1.5;">{html}</div>'
        return html

    @staticmethod
    def extract_code_blocks(text):
        blocks = []
        for match in re.finditer(r'```(w*)\n(.*?)\n```', text, re.DOTALL):
            blocks.append({"language": match.group(1) or "text", "code": match.group(2)})
        return blocks
