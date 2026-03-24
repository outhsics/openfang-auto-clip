"""
Core Agent Skills Framework

Base classes and registry for agent skills system.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path


class SkillStatus(Enum):
    """Status of skill execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SkillResult:
    """Result of skill execution"""

    success: bool
    status: SkillStatus
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }


@dataclass
class SkillContext:
    """Context for skill execution"""

    workspace: Path = field(default_factory=lambda: Path.cwd())
    config: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def get_var(self, name: str, default: Any = None) -> Any:
        """Get variable from context"""
        return self.variables.get(name, default)

    def set_var(self, name: str, value: Any):
        """Set variable in context"""
        self.variables[name] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def add_history(self, entry: Dict[str, Any]):
        """Add entry to execution history"""
        self.history.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workspace": str(self.workspace),
            "config": self.config,
            "variables": self.variables,
            "history_count": len(self.history)
        }


class Skill(ABC):
    """Base class for agent skills"""

    # Skill metadata
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    parameters: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__

    @abstractmethod
    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        Execute the skill

        Args:
            context: Execution context
            **kwargs: Skill-specific parameters

        Returns:
            SkillResult with execution outcome
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate skill parameters

        Args:
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        for param_name, param_config in self.parameters.items():
            if param_config.get("required", False) and param_name not in params:
                return False, f"Required parameter missing: {param_name}"

            # Type validation
            if param_name in params:
                expected_type = param_config.get("type")
                if expected_type and not isinstance(params[param_name], expected_type):
                    return False, f"Parameter {param_name} must be {expected_type.__name__}"

        return True, None

    def get_schema(self) -> Dict[str, Any]:
        """Get skill schema for documentation/registration"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "parameters": self.parameters
        }


class SkillRegistry:
    """Registry for agent skills"""

    _instance = None
    _skills: Dict[str, Type[Skill]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, skill_class: Type[Skill]):
        """Register a skill class"""
        instance = skill_class()
        cls._skills[instance.name] = skill_class
        return skill_class

    @classmethod
    def unregister(cls, skill_name: str):
        """Unregister a skill"""
        if skill_name in cls._skills:
            del cls._skills[skill_name]

    @classmethod
    def get(cls, skill_name: str) -> Optional[Type[Skill]]:
        """Get a skill class by name"""
        return cls._skills.get(skill_name)

    @classmethod
    def create(cls, skill_name: str) -> Optional[Skill]:
        """Create a skill instance"""
        skill_class = cls.get(skill_name)
        if skill_class:
            return skill_class()
        return None

    @classmethod
    def list_skills(cls) -> List[str]:
        """List all registered skill names"""
        return list(cls._skills.keys())

    @classmethod
    def get_all_schemas(cls) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered skills"""
        schemas = {}
        for name, skill_class in cls._skills.items():
            instance = skill_class()
            schemas[name] = instance.get_schema()
        return schemas

    @classmethod
    def export_registry(cls, path: Path):
        """Export registry to JSON file"""
        schemas = cls.get_all_schemas()
        with open(path, "w") as f:
            json.dump(schemas, f, indent=2)


# Decorator for easy skill registration
def register_skill(cls: Type[Skill]) -> Type[Skill]:
    """Decorator to register a skill class"""
    SkillRegistry.register(cls)
    return cls


class SkillExecutor:
    """Execute skills with context management"""

    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or Path.cwd()
        self.context = SkillContext(workspace=self.workspace)
        self.registry = SkillRegistry()

    def execute(
        self,
        skill_name: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> SkillResult:
        """
        Execute a skill

        Args:
            skill_name: Name of skill to execute
            params: Parameters for the skill
            timeout: Optional timeout in seconds

        Returns:
            SkillResult
        """
        import time
        start_time = time.time()

        skill = self.registry.create(skill_name)
        if not skill:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=f"Skill not found: {skill_name}"
            )

        # Validate parameters
        is_valid, error_msg = skill.validate_params(params)
        if not is_valid:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=error_msg
            )

        # Add to history
        self.context.add_history({
            "skill": skill_name,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })

        # Execute
        try:
            result = skill.execute(self.context, **params)
            result.execution_time = time.time() - start_time
            return result

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def execute_chain(
        self,
        chain: List[Dict[str, Any]],
        stop_on_error: bool = True
    ) -> List[SkillResult]:
        """
        Execute a chain of skills

        Args:
            chain: List of {"skill": name, "params": {}} dicts
            stop_on_error: Whether to stop on first error

        Returns:
            List of SkillResults
        """
        results = []

        for step in chain:
            skill_name = step.get("skill")
            params = step.get("params", {})

            result = self.execute(skill_name, params)
            results.append(result)

            # Store results in context for next skills
            if result.success:
                result_key = f"{skill_name}_result"
                self.context.set_var(result_key, result.data)

            if not result.success and stop_on_error:
                break

        return results

    def get_context(self) -> SkillContext:
        """Get current context"""
        return self.context

    def reset_context(self):
        """Reset context"""
        self.context = SkillContext(workspace=self.workspace)


if __name__ == "__main__":
    # Test basic functionality
    print("Skill Registry Test")

    @register_skill
    class TestSkill(Skill):
        name = "test_skill"
        description = "A test skill"
        parameters = {
            "message": {
                "type": str,
                "description": "Message to echo",
                "required": True
            }
        }

        def execute(self, context: SkillContext, **kwargs) -> SkillResult:
            message = kwargs.get("message", "")
            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={"echo": message}
            )

    # List registered skills
    print(f"Registered skills: {SkillRegistry.list_skills()}")

    # Get schema
    schema = TestSkill().get_schema()
    print(f"Schema: {json.dumps(schema, indent=2)}")

    # Execute
    executor = SkillExecutor()
    result = executor.execute("test_skill", {"message": "Hello!"})
    print(f"Result: {result.to_dict()}")
