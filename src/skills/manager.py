"""SkillManager - enable/disable/edit skills with chain support."""
from pathlib import Path
from src.skills.loader import SkillLoader, Skill
from src.skills.registry import SkillRegistry
from src.core.storage import Database

class SkillManager:
    def __init__(self):
        self._registry = SkillRegistry()
        self._db = Database()

    def load_bundled(self):
        bundled_dir = Path(__file__).parent / "bundled"
        if bundled_dir.exists():
            for f in bundled_dir.glob("*.py"):
                if f.stem != "__init__":
                    try:
                        mod = __import__(f"src.skills.bundled.{f.stem}", fromlist=["create_skill"])
                        skill = mod.create_skill()
                        self._registry.register(skill)
                    except Exception as e:
                        print(f"Failed to load bundled skill {f.stem}: {e}")

    def load_from_dir(self, dir_path):
        p = Path(dir_path)
        for f in p.glob("*.md"):
            skill = SkillLoader.load_skill(f)
            self._registry.register(skill)
        for f in p.glob("*.yaml"):
            skill = SkillLoader.load_skill(f)
            self._registry.register(skill)

    def enable(self, name):
        s = self._registry.get(name)
        if s: s.enabled = True

    def disable(self, name):
        s = self._registry.get(name)
        if s: s.enabled = False

    def get_chain(self, initial_skill_name):
        results = []
        name = initial_skill_name
        visited = set()
        while name and name not in visited:
            skill = self._registry.get(name)
            if not skill: break
            visited.add(name)
            results.append(skill)
            next_skills = skill.chain_to
            name = next_skills[0] if next_skills else None
        return results
