"""
使用统计和分析

提供简单的使用统计和性能分析
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from .database import get_database, TaskRecord

logger = logging.getLogger(__name__)


class UsageAnalytics:
    """使用分析器"""

    def __init__(self):
        self.db = get_database()

    def get_summary(self) -> Dict:
        """获取使用摘要"""
        stats = self.db.get_overall_stats()

        return {
            "total_tasks": stats.get('total', 0),
            "completed_tasks": stats.get('completed', 0),
            "failed_tasks": stats.get('failed', 0),
            "pending_tasks": stats.get('pending', 0),
            "total_clips": stats.get('total_clips', 0),
            "success_rate": self._calculate_success_rate(stats),
            "last_activity": stats.get('last_activity')
        }

    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """获取每日统计"""
        return self.db.get_statistics(days)

    def get_provider_usage(self) -> Dict[str, int]:
        """获取提供商使用情况"""
        tasks = self.db.list_tasks(limit=1000)

        stt_usage = {}
        tts_usage = {}

        for task in tasks:
            # STT 统计
            stt = task.stt_provider or "unknown"
            stt_usage[stt] = stt_usage.get(stt, 0) + 1

            # TTS 统计
            if task.tts_provider:
                tts = task.tts_provider
                tts_usage[tts] = tts_usage.get(tts, 0) + 1

        return {
            "stt_providers": stt_usage,
            "tts_providers": tts_usage
        }

    def get_failure_analysis(self) -> Dict:
        """获取失败分析"""
        failed_tasks = self.db.get_failed_tasks()

        # 按错误类型分组
        error_types = {}
        for task in failed_tasks:
            error = task.error or "unknown"
            error_types[error] = error_types.get(error, 0) + 1

        # 按提供商分组
        provider_failures = {}
        for task in failed_tasks:
            provider = task.stt_provider or "unknown"
            provider_failures[provider] = provider_failures.get(provider, 0) + 1

        return {
            "total_failures": len(failed_tasks),
            "error_types": error_types,
            "provider_failures": provider_failures,
            "recent_failures": [
                {
                    "task_id": t.task_id,
                    "video_url": t.video_url,
                    "error": t.error,
                    "created_at": t.created_at
                }
                for t in failed_tasks[:10]
            ]
        }

    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        # 计算平均处理时间
        completed_tasks = [
            t for t in self.db.list_tasks(limit=1000)
            if t.status == "completed" and t.completed_at
        ]

        if not completed_tasks:
            return {"average_processing_time": None}

        total_time = 0
        for task in completed_tasks:
            created = datetime.fromisoformat(task.created_at)
            completed = datetime.fromisoformat(task.completed_at)
            total_time += (completed - created).total_seconds()

        avg_time = total_time / len(completed_tasks)

        return {
            "average_processing_time": avg_time,
            "total_completed": len(completed_tasks),
            "fastest_task": min(
                (datetime.fromisoformat(t.completed_at) - datetime.fromisoformat(t.created_at)).total_seconds()
                for t in completed_tasks
            ),
            "slowest_task": max(
                (datetime.fromisoformat(t.completed_at) - datetime.fromisoformat(t.created_at)).total_seconds()
                for t in completed_tasks
            )
        }

    def get_recent_activity(self, limit: int = 20) -> List[Dict]:
        """获取最近活动"""
        tasks = self.db.get_recent_tasks(limit=limit)

        return [
            {
                "task_id": t.task_id,
                "video_url": t.video_url,
                "status": t.status,
                "created_at": t.created_at,
                "num_clips": t.num_clips,
                "stt_provider": t.stt_provider
            }
            for t in tasks
        ]

    def export_report(self, output_path: Optional[str] = None) -> str:
        """导出分析报告"""
        if output_path is None:
            output_dir = Path.home() / ".openfang" / "reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

        # 生成报告
        report_lines = [
            "# OpenFang Auto Clip - 使用分析报告",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "## 📊 总体统计\n"
        ]

        # 总体统计
        summary = self.get_summary()
        report_lines.extend([
            f"- **总任务数**: {summary['total_tasks']}",
            f"- **已完成**: {summary['completed_tasks']}",
            f"- **失败**: {summary['failed_tasks']}",
            f"- **待处理**: {summary['pending_tasks']}",
            f"- **总短片数**: {summary['total_clips']}",
            f"- **成功率**: {summary['success_rate']:.1f}%",
            f"- **最后活动**: {summary['last_activity'] or '无'}",
            ""
        ])

        # 提供商使用
        report_lines.append("## 🎤 AI 提供商使用情况\n")
        provider_usage = self.get_provider_usage()

        report_lines.append("### STT 提供商")
        for provider, count in provider_usage['stt_providers'].items():
            report_lines.append(f"- **{provider}**: {count} 次")

        if provider_usage['tts_providers']:
            report_lines.append("\n### TTS 提供商")
            for provider, count in provider_usage['tts_providers'].items():
                report_lines.append(f"- **{provider}**: {count} 次")

        # 性能指标
        report_lines.append("\n## ⚡ 性能指标\n")
        performance = self.get_performance_metrics()
        if performance['average_processing_time']:
            avg_time = performance['average_processing_time']
            report_lines.extend([
                f"- **平均处理时间**: {avg_time:.1f} 秒",
                f"- **最快任务**: {performance['fastest_task']:.1f} 秒",
                f"- **最慢任务**: {performance['slowest_task']:.1f} 秒",
                ""
            ])

        # 失败分析
        report_lines.append("## ❌ 失败分析\n")
        failure = self.get_failure_analysis()
        report_lines.append(f"总失败数: {failure['total_failures']}\n")

        if failure['error_types']:
            report_lines.append("### 错误类型")
            for error, count in failure['error_types'].items():
                report_lines.append(f"- **{error}**: {count} 次")

        # 最近活动
        report_lines.append("\n## 🕐 最近活动\n")
        recent = self.get_recent_activity(limit=10)
        for activity in recent:
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "pending": "⏳",
                "processing": "🔄"
            }.get(activity['status'], "❓")

            report_lines.append(
                f"{status_emoji} **{activity['created_at']}** - "
                f"{activity['stt_provider']} - "
                f"[{activity['task_id']}]"
            )

        # 写入文件
        report_content = "\n".join(report_lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"分析报告已导出: {output_path}")
        return output_path

    def _calculate_success_rate(self, stats: Dict) -> float:
        """计算成功率"""
        total = stats.get('total', 0)
        if total == 0:
            return 0.0

        completed = stats.get('completed', 0)
        return (completed / total) * 100


# CLI 命令
def print_analytics_summary():
    """打印分析摘要（CLI 命令）"""
    analytics = UsageAnalytics()

    print("\n" + "="*60)
    print("📊 OpenFang Auto Clip - 使用统计")
    print("="*60 + "\n")

    # 总体统计
    summary = analytics.get_summary()
    print("总体统计:")
    print(f"  总任务数: {summary['total_tasks']}")
    print(f"  已完成: {summary['completed_tasks']}")
    print(f"  失败: {summary['failed_tasks']}")
    print(f"  待处理: {summary['pending_tasks']}")
    print(f"  总短片数: {summary['total_clips']}")
    print(f"  成功率: {summary['success_rate']:.1f}%")
    print(f"  最后活动: {summary['last_activity'] or '无'}\n")

    # 提供商使用
    provider_usage = analytics.get_provider_usage()
    print("STT 提供商使用:")
    for provider, count in provider_usage['stt_providers'].items():
        print(f"  {provider}: {count} 次")
    print()

    # 性能指标
    performance = analytics.get_performance_metrics()
    if performance['average_processing_time']:
        print("性能指标:")
        print(f"  平均处理时间: {performance['average_processing_time']:.1f} 秒")
        print(f"  最快: {performance['fastest_task']:.1f} 秒")
        print(f"  最慢: {performance['slowest_task']:.1f} 秒\n")

    # 最近活动
    print("最近活动:")
    for activity in analytics.get_recent_activity(limit=5):
        status_emoji = {
            "completed": "✅",
            "failed": "❌",
            "pending": "⏳",
            "processing": "🔄"
        }.get(activity['status'], "❓")

        print(f"  {status_emoji} {activity['created_at']} - {activity['stt_provider']}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print_analytics_summary()
