"""
Utility modules for AdventureAI
"""

from .database import Database
from .dice_roller import DiceRoller
from .prompt_generator import PromptGenerator
from typing import Optional
from agents.illustrator_agent import IllustratorAgent

__all__ = [
    "Database",
    "DiceRoller",
    "PromptGenerator",
]


class ResourceManager:
    _instance = None
    _illustrator: Optional[IllustratorAgent] = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    async def initialize(cls):
        """Initialize all heavy resources"""
        instance = cls.get_instance()
        if instance._illustrator is None:
            instance._illustrator = IllustratorAgent()
            await instance._illustrator.initialize()

    @classmethod
    def get_illustrator(cls) -> Optional[IllustratorAgent]:
        return cls.get_instance()._illustrator

    @classmethod
    async def cleanup(cls):
        """Cleanup all resources"""
        instance = cls.get_instance()
        if instance._illustrator:
            await instance._illustrator.cleanup()
            instance._illustrator = None
