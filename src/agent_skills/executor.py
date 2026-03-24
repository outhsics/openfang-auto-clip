"""
Skill Executor

High-level executor for running agent skills with workflows.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .core import Skill, SkillContext, SkillResult, SkillExecutor as BaseExecutor


class Workflow:
    """Workflow for chaining multiple skills"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[Dict[str, Any]] = []
        self.variables: Dict[str, Any] = {}

    def add_step(
        self,
        skill: str,
        params: Dict[str, Any],
        condition: Optional[str] = None
    ):
        """
        Add a step to the workflow

        Args:
            skill: Name of skill to execute
            params: Parameters for the skill
            condition: Optional condition expression
        """
        self.steps.append({
            "skill": skill,
            "params": params,
            "condition": condition
        })
        return self

    def set_variable(self, name: str, value: Any):
        """Set workflow variable"""
        self.variables[name] = value
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "variables": self.variables,
            "steps": self.steps
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary"""
        workflow = cls(data["name"], data.get("description", ""))
        workflow.variables = data.get("variables", {})
        workflow.steps = data.get("steps", [])
        return workflow

    @classmethod
    def from_file(cls, path: Path) -> "Workflow":
        """Load workflow from JSON file"""
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save(self, path: Path):
        """Save workflow to JSON file"""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


class WorkflowExecutor(BaseExecutor):
    """Execute workflows with multiple skills"""

    def __init__(self, workspace: Optional[Path] = None):
        super().__init__(workspace)
        self.workflows: Dict[str, Workflow] = {}

    def register_workflow(self, workflow: Workflow):
        """Register a workflow"""
        self.workflows[workflow.name] = workflow

    def load_workflow(self, path: Path) -> Workflow:
        """Load workflow from file"""
        workflow = Workflow.from_file(path)
        self.register_workflow(workflow)
        return workflow

    def execute_workflow(
        self,
        workflow_name: str,
        variables: Optional[Dict[str, Any]] = None,
        stop_on_error: bool = True
    ) -> List[SkillResult]:
        """
        Execute a registered workflow

        Args:
            workflow_name: Name of workflow to execute
            variables: Optional variables to override
            stop_on_error: Whether to stop on first error

        Returns:
            List of SkillResults
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_name}")

        workflow = self.workflows[workflow_name]

        # Set workflow variables in context
        workflow_vars = workflow.variables.copy()
        if variables:
            workflow_vars.update(variables)

        for name, value in workflow_vars.items():
            self.context.set_var(name, value)

        # Execute steps
        results = []
        for step in workflow.steps:
            # Check condition
            condition = step.get("condition")
            if condition and not self._evaluate_condition(condition):
                continue

            # Execute skill
            skill_name = step["skill"]
            params = self._resolve_params(step["params"])

            result = self.execute(skill_name, params)
            results.append(result)

            if not result.success and stop_on_error:
                break

        return results

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate condition expression"""
        try:
            return eval(condition, {}, self.context.variables)
        except:
            return False

    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter references"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Variable reference
                var_name = value[1:]
                resolved[key] = self.context.get_var(var_name, value)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_params(value)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_params(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                resolved[key] = value
        return resolved

    def list_workflows(self) -> List[str]:
        """List registered workflow names"""
        return list(self.workflows.keys())


class Agent:
    """Agent with skills and workflows"""

    def __init__(
        self,
        name: str,
        description: str = "",
        workspace: Optional[Path] = None
    ):
        self.name = name
        self.description = description
        self.executor = WorkflowExecutor(workspace)
        self.skills: List[str] = []
        self.created_at = datetime.now().isoformat()

    def add_skill(self, skill_name: str):
        """Add a skill to this agent"""
        if skill_name not in self.skills:
            self.skills.append(skill_name)
        return self

    def add_workflow(self, workflow: Workflow):
        """Add a workflow to this agent"""
        self.executor.register_workflow(workflow)
        return self

    def execute(
        self,
        task: str,
        params: Dict[str, Any]
    ) -> SkillResult:
        """
        Execute a task (skill or workflow)

        Args:
            task: Name of skill or workflow
            params: Parameters for execution

        Returns:
            SkillResult or list of results
        """
        # Check if it's a workflow
        if task in self.executor.list_workflows():
            results = self.executor.execute_workflow(task, params)
            # Return summary
            successful = sum(1 for r in results if r.success)
            return SkillResult(
                success=successful == len(results),
                status=SkillStatus.COMPLETED,
                data={
                    "workflow": task,
                    "steps_total": len(results),
                    "steps_successful": successful,
                    "results": [r.to_dict() for r in results]
                }
            )

        # Otherwise execute as skill
        return self.executor.execute(task, params)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "skills": self.skills,
            "workflows": self.executor.list_workflows(),
            "created_at": self.created_at
        }


# Preset workflows
def create_video_processing_workflow() -> Workflow:
    """Create standard video processing workflow"""
    workflow = Workflow(
        name="video_processing",
        description="Download, transform, and extract clips from video"
    )

    workflow.add_step("video_download", {
        "url": "$video_url",
        "output_dir": "$output_dir"
    })

    workflow.add_step("video_transform", {
        "input_path": "$video_download_result.video_path",
        "transform_level": 1
    })

    workflow.add_step("clip_extract", {
        "input_path": "$video_transform_result.output_path",
        "segments": "$clip_segments"
    })

    return workflow


def create_aigc_content_workflow() -> Workflow:
    """Create AIGC content generation workflow"""
    workflow = Workflow(
        name="aigc_content",
        description="Generate AI images and videos for content"
    )

    workflow.add_step("aigc_image", {
        "prompt": "$image_prompt",
        "style": "$image_style",
        "variations": 3
    })

    workflow.add_step("aigc_video", {
        "prompt": "$video_prompt",
        "duration": 4.0
    })

    return workflow


def create_full_pipeline_workflow() -> Workflow:
    """Create full video creation pipeline workflow"""
    workflow = Workflow(
        name="full_pipeline",
        description="Complete pipeline: download -> transform -> transcript -> clips"
    )

    workflow.add_step("video_download", {
        "url": "$video_url"
    })

    workflow.add_step("video_transform", {
        "input_path": "$video_download_result.video_path",
        "preset": "cinematic"
    })

    workflow.add_step("transcript_generate", {
        "video_path": "$video_transform_result.output_path",
        "model": "base"
    })

    return workflow


if __name__ == "__main__":
    # Test workflow execution
    print("Workflow Executor Test")

    # Create executor
    executor = WorkflowExecutor()

    # Register preset workflows
    executor.register_workflow(create_video_processing_workflow())
    executor.register_workflow(create_aigc_content_workflow())
    executor.register_workflow(create_full_pipeline_workflow())

    print(f"Registered workflows: {executor.list_workflows()}")

    # Create agent
    agent = Agent("test_agent", "Test agent for video processing")
    agent.add_skill("video_download")
    agent.add_skill("video_transform")
    agent.add_workflow(create_video_processing_workflow())

    print(f"Agent: {agent.to_dict()}")
