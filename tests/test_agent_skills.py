#!/usr/bin/env python3
"""
Test agent skills module
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_skills.core import (
    Skill,
    SkillStatus,
    SkillResult,
    SkillContext,
    SkillRegistry,
    SkillExecutor
)
from src.agent_skills import (
    VideoDownloadSkill,
    VideoTransformSkill,
    AIGCImageSkill
)


class TestSkillResult(unittest.TestCase):
    """Test SkillResult dataclass"""

    def test_create_success_result(self):
        """Test creating a success result"""
        result = SkillResult(
            success=True,
            status=SkillStatus.COMPLETED,
            data={"key": "value"}
        )

        self.assertTrue(result.success)
        self.assertEqual(result.status, SkillStatus.COMPLETED)
        self.assertEqual(result.data["key"], "value")

    def test_to_dict(self):
        """Test converting result to dictionary"""
        result = SkillResult(
            success=True,
            status=SkillStatus.COMPLETED,
            execution_time=1.5
        )

        result_dict = result.to_dict()
        self.assertIn("success", result_dict)
        self.assertIn("status", result_dict)
        self.assertEqual(result_dict["execution_time"], 1.5)


class TestSkillContext(unittest.TestCase):
    """Test SkillContext"""

    def test_set_and_get_var(self):
        """Test setting and getting variables"""
        context = SkillContext()
        context.set_var("test", "value")

        self.assertEqual(context.get_var("test"), "value")

    def test_get_var_default(self):
        """Test getting variable with default value"""
        context = SkillContext()

        self.assertIsNone(context.get_var("nonexistent"))
        self.assertEqual(context.get_var("nonexistent", "default"), "default")

    def test_config_access(self):
        """Test accessing config values"""
        context = SkillContext(config={"level1": {"level2": "value"}})

        self.assertEqual(context.get_config("level1.level2"), "value")
        self.assertIsNone(context.get_config("level1.nonexistent"))

    def test_history(self):
        """Test history tracking"""
        context = SkillContext()
        context.add_history({"skill": "test", "result": "success"})

        self.assertEqual(len(context.history), 1)
        self.assertEqual(context.history[0]["skill"], "test")


class TestSkillRegistry(unittest.TestCase):
    """Test SkillRegistry"""

    def test_register_skill(self):
        """Test registering a skill"""

        @SkillRegistry.register
        class TestSkill(Skill):
            name = "test_skill"
            description = "Test skill"
            version = "1.0.0"
            author = "Test"

            def execute(self, context, **kwargs):
                return SkillResult(success=True, status=SkillStatus.COMPLETED)

        self.assertIn("test_skill", SkillRegistry.list_skills())

    def test_get_skill(self):
        """Test getting registered skill"""

        @SkillRegistry.register
        class TestSkill(Skill):
            name = "get_test"
            description = "Test"
            version = "1.0.0"
            author = "Test"

            def execute(self, context, **kwargs):
                return SkillResult(success=True, status=SkillStatus.COMPLETED)

        skill_class = SkillRegistry.get("get_test")
        self.assertIsNotNone(skill_class)

    def test_create_skill(self):
        """Test creating skill instance"""

        @SkillRegistry.register
        class TestSkill(Skill):
            name = "create_test"
            description = "Test"
            version = "1.0.0"
            author = "Test"

            def execute(self, context, **kwargs):
                return SkillResult(success=True, status=SkillStatus.COMPLETED)

        skill = SkillRegistry.create("create_test")
        self.assertIsInstance(skill, TestSkill)


class TestSkillExecutor(unittest.TestCase):
    """Test SkillExecutor"""

    def setUp(self):
        self.executor = SkillExecutor()

    @SkillRegistry.register
    class MockSkill(Skill):
        name = "mock_skill"
        description = "Mock skill"
        version = "1.0.0"
        author = "Test"

        def execute(self, context, **kwargs):
            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={"result": kwargs.get("input")}
            )

    def test_execute_skill(self):
        """Test executing a skill"""
        result = self.executor.execute("mock_skill", {"input": "test"})

        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], "test")

    def test_execute_nonexistent_skill(self):
        """Test executing nonexistent skill"""
        result = self.executor.execute("nonexistent", {})

        self.assertFalse(result.success)
        self.assertIn("not found", result.error)

    def test_execute_chain(self):
        """Test executing skill chain"""
        chain = [
            {"skill": "mock_skill", "params": {"input": "first"}},
            {"skill": "mock_skill", "params": {"input": "second"}}
        ]

        results = self.executor.execute_chain(chain)

        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.success for r in results))


class TestVideoDownloadSkill(unittest.TestCase):
    """Test VideoDownloadSkill"""

    def test_validate_params(self):
        """Test parameter validation"""
        skill = VideoDownloadSkill()

        # Missing required parameter
        is_valid, error = skill.validate_params({})
        self.assertFalse(is_valid)

        # Valid parameters
        is_valid, error = skill.validate_params({
            "url": "https://youtube.com/watch?v=test"
        })
        self.assertTrue(is_valid)

    @patch('src.agent_skills.skills.get_video_source')
    def test_execute(self, mock_get_source):
        """Test skill execution"""
        mock_source = Mock()
        mock_source.download.return_value = "/path/to/video.mp4"
        mock_get_source.return_value = mock_source

        skill = VideoDownloadSkill()
        context = SkillContext()

        result = skill.execute(context, url="https://youtube.com/watch?v=test")

        self.assertTrue(result.success)
        self.assertIn("video_path", result.data)


class TestVideoTransformSkill(unittest.TestCase):
    """Test VideoTransformSkill"""

    def test_validate_params(self):
        """Test parameter validation"""
        skill = VideoTransformSkill()

        # Missing required parameter
        is_valid, error = skill.validate_params({})
        self.assertFalse(is_valid)

        # Valid parameters
        is_valid, error = skill.validate_params({
            "input_path": "/path/to/video.mp4"
        })
        self.assertTrue(is_valid)


class TestAIGCImageSkill(unittest.TestCase):
    """Test AIGCImageSkill"""

    def test_validate_params(self):
        """Test parameter validation"""
        skill = AIGCImageSkill()

        # Missing required parameter
        is_valid, error = skill.validate_params({})
        self.assertFalse(is_valid)

        # Valid parameters
        is_valid, error = skill.validate_params({
            "prompt": "A beautiful landscape"
        })
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()
