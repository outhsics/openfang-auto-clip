"""
本地数据管理使用示例

演示如何使用本地数据库和统计分析
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhancements.data_management import (
    get_database,
    LocalDatabase,
    TaskRecord,
    UsageAnalytics,
    print_analytics_summary
)


def example_create_task():
    """示例 1: 创建任务记录"""
    print("\n📝 示例 1: 创建任务记录")

    db = get_database()

    # 创建新任务
    task = db.create_task(
        task_id="task_001",
        video_url="https://www.youtube.com/watch?v=example",
        num_clips=5,
        stt_provider="groq_whisper",
        tts_provider="edge_tts",
        metadata={"quality": "high", "duration": 120}
    )

    print(f"✅ 任务已创建!")
    print(f"  任务 ID: {task.task_id}")
    print(f"  状态: {task.status}")
    print(f"  创建时间: {task.created_at}")


def example_update_task_status():
    """示例 2: 更新任务状态"""
    print("\n🔄 示例 2: 更新任务状态")

    db = get_database()

    # 更新任务状态为处理中
    success = db.update_task_status(
        task_id="task_001",
        status="processing"
    )

    if success:
        print("✅ 状态已更新为: processing")

    # 模拟完成
    success = db.update_task_status(
        task_id="task_001",
        status="completed",
        output_dir="/path/to/output"
    )

    if success:
        print("✅ 状态已更新为: completed")


def example_get_task():
    """示例 3: 获取任务信息"""
    print("\n🔍 示例 3: 获取任务信息")

    db = get_database()

    task = db.get_task("task_001")

    if task:
        print(f"✅ 找到任务:")
        print(f"  视频 URL: {task.video_url}")
        print(f"  状态: {task.status}")
        print(f"  STT 提供商: {task.stt_provider}")
        print(f"  TTS 提供商: {task.tts_provider}")
        print(f"  短片数量: {task.num_clips}")


def example_list_tasks():
    """示例 4: 列出任务"""
    print("\n📋 示例 4: 列出任务")

    db = get_database()

    # 获取最近的任务
    recent_tasks = db.get_recent_tasks(limit=10)

    print(f"✅ 最近 {len(recent_tasks)} 个任务:")
    for task in recent_tasks:
        status_emoji = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(task.status, "❓")

        print(f"  {status_emoji} {task.task_id} - {task.status}")

    # 获取失败的任务
    failed_tasks = db.get_failed_tasks()
    print(f"\n❌ 失败的任务: {len(failed_tasks)}")


def example_statistics():
    """示例 5: 统计信息"""
    print("\n📊 示例 5: 统计信息")

    db = get_database()

    # 获取总体统计
    stats = db.get_overall_stats()

    print("总体统计:")
    print(f"  总任务数: {stats.get('total', 0)}")
    print(f"  已完成: {stats.get('completed', 0)}")
    print(f"  失败: {stats.get('failed', 0)}")
    print(f"  待处理: {stats.get('pending', 0)}")
    print(f"  总短片数: {stats.get('total_clips', 0)}")

    # 计算成功率
    total = stats.get('total', 0)
    if total > 0:
        success_rate = (stats.get('completed', 0) / total) * 100
        print(f"  成功率: {success_rate:.1f}%")


def example_config_management():
    """示例 6: 配置管理"""
    print("\n⚙️  示例 6: 配置管理")

    db = get_database()

    # 保存配置
    db.set_config("default_stt", "groq_whisper")
    db.set_config("default_tts", "edge_tts")
    db.set_config("auto_publish", True)
    db.set_config("telegram_chat_id", "@my_channel")

    print("✅ 配置已保存")

    # 读取配置
    default_stt = db.get_config("default_stt", "local_whisper")
    auto_publish = db.get_config("auto_publish", False)

    print(f"\n当前配置:")
    print(f"  默认 STT: {default_stt}")
    print(f"  自动发布: {auto_publish}")

    # 获取所有配置
    all_config = db.get_all_config()
    print(f"\n所有配置: {all_config}")


def example_analytics():
    """示例 7: 使用分析"""
    print("\n📈 示例 7: 使用分析")

    analytics = UsageAnalytics()

    # 获取摘要
    summary = analytics.get_summary()

    print("使用摘要:")
    print(f"  总任务数: {summary['total_tasks']}")
    print(f"  成功率: {summary['success_rate']:.1f}%")
    print(f"  最后活动: {summary['last_activity']}")

    # 获取提供商使用情况
    provider_usage = analytics.get_provider_usage()

    print("\nSTT 提供商使用:")
    for provider, count in provider_usage['stt_providers'].items():
        print(f"  {provider}: {count} 次")

    # 获取性能指标
    performance = analytics.get_performance_metrics()
    if performance['average_processing_time']:
        print(f"\n性能指标:")
        print(f"  平均处理时间: {performance['average_processing_time']:.1f} 秒")
        print(f"  最快: {performance['fastest_task']:.1f} 秒")
        print(f"  最慢: {performance['slowest_task']:.1f} 秒")


def example_export_report():
    """示例 8: 导出分析报告"""
    print("\n📄 示例 8: 导出分析报告")

    analytics = UsageAnalytics()

    # 导出 Markdown 报告
    report_path = analytics.export_report()

    print(f"✅ 报告已导出: {report_path}")


def example_cleanup():
    """示例 9: 清理旧数据"""
    print("\n🧹 示例 9: 清理旧数据")

    db = get_database()

    # 清理 30 天前的已完成和失败任务
    deleted = db.cleanup_old_tasks(days=30)

    print(f"✅ 已清理 {deleted} 个旧任务")

    # 优化数据库
    db.vacuum()
    print("✅ 数据库已优化")


def example_batch_operations():
    """示例 10: 批量操作"""
    print("\n📦 示例 10: 批量操作")

    db = get_database()

    # 批量创建任务
    video_urls = [
        "https://www.youtube.com/watch?v=video1",
        "https://www.youtube.com/watch?v=video2",
        "https://www.youtube.com/watch?v=video3"
    ]

    print(f"创建 {len(video_urls)} 个任务...")

    for i, url in enumerate(video_urls, 1):
        task = db.create_task(
            task_id=f"batch_task_{i}",
            video_url=url,
            num_clips=3,
            stt_provider="local_whisper"
        )
        print(f"  ✅ {task.task_id}")

    # 批量更新状态
    print("\n批量更新状态...")
    for i in range(1, len(video_urls) + 1):
        db.update_task_status(
            task_id=f"batch_task_{i}",
            status="completed"
        )

    print("✅ 所有任务已完成")


def main():
    """运行所有示例"""
    print("="*60)
    print("💾 本地数据管理示例")
    print("="*60)

    # 运行示例
    try:
        example_create_task()
        example_update_task_status()
        example_get_task()
        example_list_tasks()
        example_statistics()
        example_config_management()
        example_analytics()
        # example_export_report()  # 需要实际数据
        # example_cleanup()  # 会删除数据，谨慎使用
        example_batch_operations()

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
