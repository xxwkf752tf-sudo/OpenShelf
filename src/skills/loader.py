"""SkillLoader - load .md/.yaml skill files."""
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class Skill:
    name: str
    description: str = ""
    instructions: str = ""
    allowed_tools: list = field(default_factory=list)
    examples: list = field(default_factory=list)
    chain_to: list = field(default_factory=list)
    enabled: bool = True
    source_path: str = ""

class SkillLoader:
    @staticmethod
    def load_skill(filepath):
        p = Path(filepath)
        content = p.read_text(encoding="utf-8")
        if p.suffix in (".yaml",".yml"):
            return SkillLoader._from_yaml(content, p)
        return SkillLoader._from_markdown(content, p)

    @staticmethod
    def _from_markdown(content, path):
        parts = content.split("---", 2)
        meta, body = {}, content
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            body = parts[2].strip()
        return Skill(name=meta.get("name",path.stem), description=meta.get("description",""), instructions=body, allowed_tools=meta.get("allowed_tools",[]), examples=meta.get("examples",[]), chain_to=meta.get("chain_to",[]), source_path=str(path))

    @staticmethod
    def _from_yaml(content, path):
        data = yaml.safe_load(content) or {}
        return Skill(name=data.get("name",path.stem), description=data.get("description",""), instructions=data.get("instructions",""), allowed_tools=data.get("allowed_tools",[]), examples=data.get("examples",[]), chain_to=data.get("chain_to",[]), source_path=str(path))
