#!/usr/bin/env python3
"""
Error Handling System - Examples and Tests

This script demonstrates the error handling and recovery system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_clip.error_handling import (
    ErrorHandler,
    CheckpointManager,
    ResumableOperation,
    GracefulDegradation,
    ValidatedOperation,
    PartialRecoveryManager,
    error_handling_context,
    handle_with_retry,
    safe_execute,
    TranscriptError,
    ResourceError,
)


def example_1_basic_error_handling():
    """Example 1: Basic error handling"""
    print("=" * 70)
    print("Example 1: Basic Error Handling")
    print("=" * 70)

    error_handler = ErrorHandler()

    try:
        # Simulate an error
        raise TranscriptError("Transcript parsing failed", line=42)
    except Exception as e:
        error_info = error_handler.handle_error(e)
        print(f"✅ Error handled: {error_info.message}")
        print(f"   Category: {error_info.category.value}")
        print(f"   Severity: {error_info.severity.value}")

    # Get summary
    summary = error_handler.get_error_summary()
    print(f"\n📊 Error Summary:")
    print(f"   Total: {summary['total_errors']}")
    print(f"   Recoverable: {summary['recoverable']}")


def example_2_checkpoint_system():
    """Example 2: Checkpoint and resume"""
    print("\n" + "=" * 70)
    print("Example 2: Checkpoint & Resume System")
    print("=" * 70)

    checkpoint_mgr = CheckpointManager()
    operation_id = "test_operation_001"

    # Simulate a multi-step operation
    class MyOperation(ResumableOperation):
        def __init__(self, operation_id, checkpoint_manager):
            super().__init__(operation_id, checkpoint_manager)
            self.total_steps = 5

        def run(self):
            for i in range(1, 6):
                step_id = f"step_{i}"

                # Skip if already completed
                if self.is_step_completed(step_id):
                    print(f"   ⏭️  Skipping {step_id} (already completed)")
                    continue

                # Simulate work
                print(f"   🔄 Processing {step_id}...")

                # Save checkpoint
                self.complete_step(step_id)

                # Show progress
                progress = self.get_progress()
                print(f"   📊 Progress: {progress['progress_percent']:.0f}%")

    # Create and run operation
    operation = MyOperation(operation_id, checkpoint_mgr)

    print("\n📋 First run:")
    operation.run()

    print("\n📋 Second run (should skip completed steps):")
    operation.run()

    # Cleanup
    operation.cleanup()
    print("\n✅ Checkpoint system working!")


def example_3_graceful_degradation():
    """Example 3: Graceful degradation with fallbacks"""
    print("\n" + "=" * 70)
    print("Example 3: Graceful Degradation")
    print("=" * 70)

    # Primary function (might fail)
    def primary_function():
        print("   🔄 Trying primary function...")
        # Simulate failure
        raise ValueError("Primary function unavailable")

    # Fallback function
    def fallback_function():
        print("   🔄 Using fallback function...")
        return "Fallback result"

    # With fallback
    result = GracefulDegradation.with_fallback(
        primary_function,
        fallback_function,
        (ValueError,)
    )

    print(f"   ✅ Result: {result}")

    # With default value
    def risky_function():
        print("   🔄 Trying risky function...")
        raise RuntimeError("Failed")

    default_result = GracefulDegradation.with_default(
        risky_function,
        "Default Value",
        (RuntimeError,)
    )

    print(f"   ✅ Result: {default_result}")


def example_4_retry_with_backoff():
    """Example 4: Retry with exponential backoff"""
    print("\n" + "=" * 70)
    print("Example 4: Retry with Backoff")
    print("=" * 70)

    # Function that fails initially
    attempt_count = [0]

    def flaky_function():
        attempt_count[0] += 1
        print(f"   🔄 Attempt {attempt_count[0]}...")

        if attempt_count[0] < 3:
            raise ConnectionError("Connection failed")

        print("   ✅ Success!")
        return "Finally succeeded"

    # Execute with retry
    result = GracefulDegradation.retry_with_backoff(
        func=flaky_function,
        max_retries=5,
        backoff_factor=0.1,  # Short delay for demo
        error_types=(ConnectionError,)
    )

    print(f"   ✅ Result: {result}")


@handle_with_retry(max_retries=3)
def example_5_retry_decorator():
    """Example 5: Using retry decorator"""
    print("\n" + "=" * 70)
    print("Example 5: Retry Decorator")
    print("=" * 70)

    call_count = [0]

    @handle_with_retry(max_retries=3)
    def unreliable_function():
        call_count[0] += 1
        print(f"   🔄 Call {call_count[0]}...")

        if call_count[0] < 2:
            raise IOError("Temporary failure")

        return "Success!"

    result = unreliable_function()
    print(f"   ✅ Result: {result}")


def example_6_validation():
    """Example 6: Input validation with recovery"""
    print("\n" + "=" * 70)
    print("Example 6: Validation with Recovery")
    print("=" * 70)

    from auto_clip import OUTPUT_DIR

    validator = ValidatedOperation(ErrorHandler())

    # Validate existing file
    demo_transcript = Path(__file__).parent.parent / "examples" / "demo" / "sample_level2_transcript.srt"

    print(f"\n📝 Validating: {demo_transcript.name}")
    is_valid = validator.validate_transcript(demo_transcript)

    if is_valid:
        print("   ✅ Transcript valid!")
    else:
        print("   ❌ Transcript validation failed")

    # Check FFmpeg
    print(f"\n🔧 Checking FFmpeg...")
    has_ffmpeg = validator.validate_ffmpeg()
    print(f"   {'✅' if has_ffmpeg else '❌'} FFmpeg {'available' if has_ffmpeg else 'not found'}")

    # Get report
    report = validator.get_report()
    print(f"\n📊 Validation Report:")
    print(f"   Warnings: {len(report['warnings'])}")
    print(f"   Fixes Applied: {len(report['fixes_applied'])}")
    print(f"   Can Proceed: {report['can_proceed']}")


def example_7_partial_recovery():
    """Example 7: Partial recovery mode"""
    print("\n" + "=" * 70)
    print("Example 7: Partial Recovery")
    print("=" * 70)

    from auto_clip import OUTPUT_DIR

    recovery_mgr = PartialRecoveryManager(OUTPUT_DIR)

    # Simulate operation with some failures
    # Define operations as functions
    def step1():
        return "Result 1"

    def step2():
        raise ValueError("Failed")

    def step3():
        return "Result 3"

    operations = [
        ("step1", step1),
        ("step2", step2),
        ("step3", step3),
    ]

    for op_name, op_func in operations:
        try:
            result = op_func()
            recovery_mgr.save_partial_result(op_name, result, {"status": "success"})
            print(f"   ✅ {op_name}: {result}")
        except Exception as e:
            recovery_mgr.record_failure(op_name, e)
            print(f"   ❌ {op_name}: {e}")

    # Get recovery summary
    summary = recovery_mgr.get_recovery_summary()
    print(f"\n📊 Recovery Summary:")
    print(f"   Succeeded: {summary['succeeded_count']}")
    print(f"   Failed: {summary['failed_count']}")
    print(f"   Completion: {summary['completion_rate']:.1%}")
    print(f"   Can Use Partial: {summary['can_use_partial']}")


def example_8_context_manager():
    """Example 8: Using error handling context manager"""
    print("\n" + "=" * 70)
    print("Example 8: Context Manager")
    print("=" * 70)

    def risky_operation(context):
        # Access handlers
        error_handler = context["error_handler"]
        checkpoint_mgr = context["checkpoint_manager"]

        # Use them
        try:
            raise ResourceError("Simulated resource failure")
        except Exception as e:
            error_handler.handle_error(e, {"operation": "test"})

    # Run with context
    with error_handling_context("test_operation", OUTPUT_DIR) as context:
        risky_operation(context)

    print("   ✅ Operation handled gracefully")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("🚀 Error Handling System - Examples & Tests")
    print("🚀 错误处理系统 - 示例和测试")
    print("=" * 70)

    try:
        example_1_basic_error_handling()
        example_2_checkpoint_system()
        example_3_graceful_degradation()
        example_4_retry_with_backoff()
        example_5_retry_decorator()
        example_6_validation()
        example_7_partial_recovery()
        example_8_context_manager()

        print("\n" + "=" * 70)
        print("✅ All Examples Completed Successfully!")
        print("✅ 所有示例成功完成！")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
