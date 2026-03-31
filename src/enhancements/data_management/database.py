"""
本地数据管理 - SQLite 数据库

用于存储任务历史、配置和使用统计
"""

import os
import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TaskRecord:
    """任务记录"""
    id: Optional[int]
    task_id: str
    video_url: str
    status: str  # pending, processing, completed, failed
    created_at: str
    completed_at: Optional[str]
    num_clips: int
    stt_provider: str
    tts_provider: Optional[str]
    output_dir: str
    error: Optional[str]
    metadata: Optional[str]  # JSON string


class LocalDatabase:
    """本地 SQLite 数据库"""

    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库

        Args:
            db_path: 数据库文件路径，默认为 ~/.openfang/tasks.db
        """
        if db_path is None:
            openfang_dir = Path.home() / ".openfang"
            openfang_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(openfang_dir / "tasks.db")

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"数据库已连接: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def _create_tables(self):
        """创建数据表"""
        cursor = self.conn.cursor()

        # 任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                video_url TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                num_clips INTEGER DEFAULT 0,
                stt_provider TEXT DEFAULT 'local_whisper',
                tts_provider TEXT,
                output_dir TEXT,
                error TEXT,
                metadata TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_id ON tasks(task_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at)
        """)

        # 统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                failed_tasks INTEGER DEFAULT 0,
                total_clips INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0,
                metadata TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        """)

        # 配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        logger.info("数据表已创建")

    # ========== 任务管理 ==========

    def create_task(
        self,
        task_id: str,
        video_url: str,
        num_clips: int = 5,
        stt_provider: str = "local_whisper",
        tts_provider: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> TaskRecord:
        """创建新任务"""
        cursor = self.conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        try:
            cursor.execute("""
                INSERT INTO tasks (
                    task_id, video_url, status, created_at,
                    num_clips, stt_provider, tts_provider, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, video_url, "pending", now,
                num_clips, stt_provider, tts_provider, metadata_json
            ))

            self.conn.commit()

            return TaskRecord(
                id=cursor.lastrowid,
                task_id=task_id,
                video_url=video_url,
                status="pending",
                created_at=now,
                completed_at=None,
                num_clips=num_clips,
                stt_provider=stt_provider,
                tts_provider=tts_provider,
                output_dir=None,
                error=None,
                metadata=metadata_json
            )

        except sqlite3.IntegrityError:
            logger.warning(f"任务已存在: {task_id}")
            return self.get_task(task_id)

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """获取任务"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()

        if row:
            return TaskRecord(**dict(row))
        return None

    def update_task_status(
        self,
        task_id: str,
        status: str,
        output_dir: Optional[str] = None,
        error: Optional[str] = None
    ) -> bool:
        """更新任务状态"""
        cursor = self.conn.cursor()

        update_fields = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

        if status == "completed":
            update_fields["completed_at"] = datetime.now().isoformat()

        if output_dir:
            update_fields["output_dir"] = output_dir

        if error:
            update_fields["error"] = error

        # 构建 SQL
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [task_id]

        cursor.execute(f"""
            UPDATE tasks SET {set_clause}
            WHERE task_id = ?
        """, values)

        self.conn.commit()
        return cursor.rowcount > 0

    def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskRecord]:
        """列出任务"""
        cursor = self.conn.cursor()

        query = "SELECT * FROM tasks"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [TaskRecord(**dict(row)) for row in rows]

    def get_recent_tasks(self, limit: int = 10) -> List[TaskRecord]:
        """获取最近的任务"""
        return self.list_tasks(limit=limit)

    def get_failed_tasks(self, limit: int = 50) -> List[TaskRecord]:
        """获取失败的任务"""
        return self.list_tasks(status="failed", limit=limit)

    # ========== 统计 ==========

    def update_statistics(
        self,
        date: Optional[str] = None,
        total_tasks: int = 0,
        completed_tasks: int = 0,
        failed_tasks: int = 0,
        total_clips: int = 0,
        total_duration: float = 0
    ):
        """更新统计"""
        cursor = self.conn.cursor()

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            INSERT OR REPLACE INTO statistics (
                date, total_tasks, completed_tasks, failed_tasks,
                total_clips, total_duration, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            date, total_tasks, completed_tasks, failed_tasks,
            total_clips, total_duration, datetime.now().isoformat()
        ))

        self.conn.commit()

    def get_statistics(self, days: int = 30) -> List[Dict]:
        """获取统计信息"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM statistics
            ORDER BY date DESC
            LIMIT ?
        """, (days,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_overall_stats(self) -> Dict:
        """获取总体统计"""
        cursor = self.conn.cursor()

        # 任务统计
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(num_clips) as total_clips
            FROM tasks
        """)

        task_stats = dict(cursor.fetchone())

        # 最近活动
        cursor.execute("""
            SELECT created_at
            FROM tasks
            ORDER BY created_at DESC
            LIMIT 1
        """)

        last_activity = cursor.fetchone()
        task_stats['last_activity'] = last_activity['created_at'] if last_activity else None

        return task_stats

    # ========== 配置管理 ==========

    def set_config(self, key: str, value: Any):
        """设置配置"""
        cursor = self.conn.cursor()

        value_str = json.dumps(value) if not isinstance(value, str) else value

        cursor.execute("""
            INSERT OR REPLACE INTO config (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value_str, datetime.now().isoformat()))

        self.conn.commit()

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()

        if row:
            try:
                return json.loads(row['value'])
            except:
                return row['value']

        return default

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM config")
        rows = cursor.fetchall()

        config = {}
        for row in rows:
            try:
                config[row['key']] = json.loads(row['value'])
            except:
                config[row['key']] = row['value']

        return config

    # ========== 维护 ==========

    def cleanup_old_tasks(self, days: int = 30):
        """清理旧任务"""
        cursor = self.conn.cursor()

        cursor.execute("""
            DELETE FROM tasks
            WHERE created_at < datetime('now', '-' || ? || ' days')
            AND status IN ('completed', 'failed')
        """, (days,))

        deleted = cursor.rowcount
        self.conn.commit()

        logger.info(f"清理了 {deleted} 个旧任务")
        return deleted

    def vacuum(self):
        """优化数据库"""
        cursor = self.conn.cursor()
        cursor.execute("VACUUM")
        self.conn.commit()
        logger.info("数据库已优化")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")


# 便捷函数
_default_db: Optional[LocalDatabase] = None


def get_database(db_path: Optional[str] = None) -> LocalDatabase:
    """获取数据库实例（单例）"""
    global _default_db

    if _default_db is None:
        _default_db = LocalDatabase(db_path)

    return _default_db
