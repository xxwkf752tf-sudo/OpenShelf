"""Tool ABC - base class for all tools in OpenShelf."""
from abc import ABC, abstractmethod

class Tool(ABC):
    name: str = ""
    description: str = ""
    parameters_schema: dict = {"type":"object","properties":{},"required":[]}

    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        ...

    def to_schema(self):
        return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":self.parameters_schema}}
