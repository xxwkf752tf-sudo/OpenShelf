"""SkillRegistry - register and discover skills."""
class SkillRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills = {}
        return cls._instance

    def register(self, skill):
        self._skills[skill.name] = skill

    def get(self, name):
        return self._skills.get(name)

    def list_all(self):
        return list(self._skills.values())

    def get_enabled(self):
        return [s for s in self._skills.values() if s.enabled]

    def get_instructions(self):
        return [s.instructions for s in self._skills.values() if s.enabled]

    def unregister(self, name):
        self._skills.pop(name, None)
