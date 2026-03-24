#!/usr/bin/env python3
"""
Agent Skills Example Scripts

Demonstrates various capabilities of the Agent Skills System.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_skills import (
    SkillExecutor,
    Workflow,
    WorkflowExecutor,
    Agent,
    create_video_processing_workflow,
    create_aigc_content_workflow,
    create_full_pipeline_workflow
)


def example_1_basic_skill_execution():
    """Example 1: Execute a single skill"""
    print("\n=== Example 1: Basic Skill Execution ===\n")

    executor = SkillExecutor()

    # Execute video download skill (dry run example)
    result = executor.execute(
        skill_name="video_download",
        params={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "output_dir": "./downloads"
        }
    )

    if result.success:
        print(f"✅ Success!")
        print(f"   Data: {result.data}")
    else:
        print(f"❌ Failed: {result.error}")


def example_2_skill_chain():
    """Example 2: Chain multiple skills"""
    print("\n=== Example 2: Skill Chain ===\n")

    executor = SkillExecutor()

    # Create a chain of skills
    chain = [
        {
            "skill": "video_download",
            "params": {
                "url": "https://www.youtube.com/watch?v=EXAMPLE"
            }
        },
        {
            "skill": "video_transform",
            "params": {
                "input_path": "$video_download_result.video_path",
                "preset": "cinematic"
            }
        },
        {
            "skill": "clip_extract",
            "params": {
                "input_path": "$video_transform_result.output_path",
                "segments": [(0, 30), (60, 90)]
            }
        }
    ]

    results = executor.execute_chain(chain)

    print(f"Executed {len(results)} skills:")
    for i, result in enumerate(results):
        status = "✅" if result.success else "❌"
        print(f"  {status} Step {i+1}: {result.status.value}")


def example_3_custom_workflow():
    """Example 3: Create and execute custom workflow"""
    print("\n=== Example 3: Custom Workflow ===\n")

    # Create workflow
    workflow = Workflow(
        name="demo_workflow",
        description="Demonstration workflow"
    )

    # Add steps
    workflow.add_step("video_download", {
        "url": "$video_url"
    })

    workflow.add_step("video_transform", {
        "input_path": "$video_download_result.video_path",
        "preset": "$preset"
    })

    # Save workflow
    workflow_path = Path("demo_workflow.json")
    workflow.save(workflow_path)
    print(f"✅ Workflow saved to: {workflow_path}")

    # Load and execute
    executor = WorkflowExecutor()
    executor.load_workflow(workflow_path)

    print(f"✅ Loaded workflow: {workflow.name}")
    print(f"   Steps: {len(workflow.steps)}")


def example_4_agent_with_workflow():
    """Example 4: Create agent with workflows"""
    print("\n=== Example 4: Agent with Workflows ===\n")

    # Create agent
    agent = Agent(
        name="video_agent",
        description="Specialized video processing agent"
    )

    # Add skills
    agent.add_skill("video_download")
    agent.add_skill("video_transform")
    agent.add_skill("batch_process")

    # Add preset workflows
    agent.add_workflow(create_video_processing_workflow())
    agent.add_workflow(create_aigc_content_workflow())

    print(f"✅ Agent created: {agent.name}")
    print(f"   Skills: {agent.skills}")
    print(f"   Workflows: {agent.to_dict()['workflows']}")


def example_5_context_variables():
    """Example 5: Using context variables"""
    print("\n=== Example 5: Context Variables ===\n")

    executor = SkillExecutor()

    # Set variables
    executor.context.set_var("api_key", "your-api-key")
    executor.context.set_var("output_format", "mp4")
    executor.context.set_var("quality", "best")

    print(f"✅ Set {len(executor.context.variables)} variables")

    # Get variable
    api_key = executor.context.get_var("api_key")
    print(f"   API Key: {api_key[:10]}...")

    # Use in skill execution
    result = executor.execute("video_download", {
        "url": "https://example.com/video.mp4",
        "quality": "$quality"
    })


def example_6_error_handling():
    """Example 6: Error handling in workflows"""
    print("\n=== Example 6: Error Handling ===\n")

    executor = WorkflowExecutor()

    # Create workflow with potential errors
    workflow = Workflow(
        name="error_demo",
        description="Demonstrate error handling"
    )

    workflow.add_step("video_download", {
        "url": "https://invalid-url-that-will-fail.com"
    })

    workflow.add_step("video_transform", {
        "input_path": "$video_download_result.video_path"
    })

    executor.register_workflow(workflow)

    # Execute with stop_on_error=True
    print("Executing with stop_on_error=True:")
    results = executor.execute_workflow(
        workflow_name="error_demo",
        stop_on_error=True
    )

    print(f"   Steps completed: {len(results)}")
    for i, result in enumerate(results):
        status = "✅" if result.success else "❌"
        print(f"   {status} Step {i+1}: {result.status.value}")
        if not result.success:
            print(f"      Error: {result.error}")


def example_7_parallel_batch():
    """Example 7: Parallel batch processing"""
    print("\n=== Example 7: Parallel Batch Processing ===\n")

    executor = SkillExecutor()

    # Execute batch skill
    result = executor.execute("batch_process", {
        "urls": [
            "https://youtube.com/watch?v=1",
            "https://youtube.com/watch?v=2",
            "https://youtube.com/watch?v=3"
        ],
        "transform_level": 1,
        "parallel": 2
    })

    if result.success:
        summary = result.data.get("summary", {})
        print(f"✅ Batch processing complete")
        print(f"   Total: {summary.get('total', 0)}")
        print(f"   Successful: {summary.get('successful', 0)}")
        print(f"   Failed: {summary.get('failed', 0)}")
    else:
        print(f"❌ Batch processing failed: {result.error}")


def example_8_aigc_workflow():
    """Example 8: AIGC content generation workflow"""
    print("\n=== Example 8: AIGC Workflow ===\n")

    agent = Agent("aigc_agent")
    agent.add_workflow(create_aigc_content_workflow())

    # Execute AIGC workflow
    result = agent.execute("aigc_content", {
        "image_prompt": "Futuristic city with neon lights",
        "image_style": "cyberpunk",
        "video_prompt": "Clouds moving over mountains"
    })

    if result.success:
        print(f"✅ AIGC workflow complete")
        print(f"   Steps: {result.data['steps_total']}")
        print(f"   Successful: {result.data['steps_successful']}")
    else:
        print(f"❌ AIGC workflow failed: {result.error}")


def example_9_custom_skill():
    """Example 9: Create and use custom skill"""
    print("\n=== Example 9: Custom Skill ===\n")

    from src.agent_skills import Skill, SkillContext, SkillResult, SkillStatus, register_skill

    @register_skill
    class GreetingSkill(Skill):
        """A simple greeting skill"""

        name = "greeting"
        description = "Greet the user"
        version = "1.0.0"
        author = "OpenFang"

        parameters = {
            "name": {
                "type": str,
                "description": "Name to greet",
                "required": True
            }
        }

        def execute(self, context: SkillContext, **kwargs) -> SkillResult:
            name = kwargs.get("name", "World")
            greeting = f"Hello, {name}!"

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={"greeting": greeting}
            )

    # Use the custom skill
    executor = SkillExecutor()
    result = executor.execute("greeting", {"name": "OpenFang User"})

    if result.success:
        print(f"✅ {result.data['greeting']}")


def example_10_workflow_serialization():
    """Example 10: Save and load workflows"""
    print("\n=== Example 10: Workflow Serialization ===\n")

    # Create workflow
    workflow = Workflow(
        name="serializable_workflow",
        description="Demonstrates workflow save/load"
    )

    workflow.add_step("video_download", {"url": "$url"})
    workflow.add_step("video_transform", {
        "input_path": "$video_download_result.video_path"
    })

    # Save to file
    workflow_path = Path("example_workflow.json")
    workflow.save(workflow_path)
    print(f"✅ Workflow saved: {workflow_path}")

    # Load from file
    loaded_workflow = Workflow.from_file(workflow_path)
    print(f"✅ Workflow loaded: {loaded_workflow.name}")
    print(f"   Steps: {len(loaded_workflow.steps)}")

    # Clean up
    workflow_path.unlink()


def example_11_agent_memory():
    """Example 11: Agent execution history"""
    print("\n=== Example 11: Agent Execution History ===\n")

    executor = SkillExecutor()

    # Execute some skills
    executor.execute("video_download", {"url": "https://example.com/1"})
    executor.execute("video_download", {"url": "https://example.com/2"})
    executor.execute("video_transform", {"input_path": "test.mp4"})

    # Check history
    history_count = len(executor.context.history)
    print(f"✅ Execution history: {history_count} entries")

    for i, entry in enumerate(executor.context.history[-3:]):
        print(f"   {i+1}. {entry['skill']} at {entry['timestamp'][:19]}")


def example_12_full_pipeline():
    """Example 12: Complete video creation pipeline"""
    print("\n=== Example 12: Full Pipeline ===\n")

    agent = Agent("pipeline_agent")
    agent.add_workflow(create_full_pipeline_workflow())

    # Execute full pipeline
    result = agent.execute("full_pipeline", {
        "video_url": "https://www.youtube.com/watch?v=EXAMPLE",
        "preset": "cinematic"
    })

    if result.success:
        print(f"✅ Full pipeline executed")
        print(f"   Steps completed: {result.data['steps_successful']}/{result.data['steps_total']}")
    else:
        print(f"❌ Pipeline failed: {result.error}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("OpenFang Auto Clip - Agent Skills Examples")
    print("=" * 60)

    examples = [
        ("Basic Skill Execution", example_1_basic_skill_execution),
        ("Skill Chain", example_2_skill_chain),
        ("Custom Workflow", example_3_custom_workflow),
        ("Agent with Workflows", example_4_agent_with_workflow),
        ("Context Variables", example_5_context_variables),
        ("Error Handling", example_6_error_handling),
        ("Parallel Batch", example_7_parallel_batch),
        ("AIGC Workflow", example_8_aigc_workflow),
        ("Custom Skill", example_9_custom_skill),
        ("Workflow Serialization", example_10_workflow_serialization),
        ("Agent Memory", example_11_agent_memory),
        ("Full Pipeline", example_12_full_pipeline),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nOptions:")
    print("  all   - Run all examples")
    print("  1-12  - Run specific example")
    print("  q     - Quit")

    choice = input("\nSelect example to run: ").strip().lower()

    if choice == "q":
        print("Goodbye!")
        return

    if choice == "all":
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        idx = int(choice) - 1
        name, func = examples[idx]
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
