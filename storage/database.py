"""
SQLite 数据库存储

功能：
- 学生信息管理
- 消息队列存储
- 课程和作业记录
- 贡献和荣誉记录
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class Database:
    """SQLite 数据库管理器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "students.db"
        self._ensure_data_dir()
        self._init_tables()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn
    
    def _init_tables(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 学生基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                union_id TEXT UNIQUE,
                level TEXT DEFAULT 'L1',
                status TEXT DEFAULT '在读',
                contact_channel TEXT,
                contact_address TEXT,
                public_key TEXT,
                encrypted_private_key TEXT,
                badge_png TEXT,
                badge_svg TEXT,
                enrolled_at TEXT NOT NULL,
                graduated_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        ''')
        
        # 学术记录表（不可篡改）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS academic_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                record_type TEXT NOT NULL,
                record_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                signature TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # 贡献记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                contribution_type TEXT NOT NULL,
                title TEXT,
                url TEXT,
                timestamp TEXT NOT NULL,
                verified_by TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # 荣誉记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS honors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                honor_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                awarded_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # 消息队列表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                encrypted_content TEXT NOT NULL,
                nonce TEXT NOT NULL,
                tag TEXT NOT NULL,
                encrypted_aes_key TEXT,
                sender_signature TEXT,
                msg_type TEXT DEFAULT 'text',
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                read_at TEXT,
                FOREIGN KEY (to_id) REFERENCES students(student_id)
            )
        ''')
        
        # 课程表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                level TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 作业表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id TEXT PRIMARY KEY,
                course_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
        ''')
        
        # 作业提交表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                submission_url TEXT,
                submitted_at TEXT NOT NULL,
                score INTEGER,
                feedback TEXT,
                graded_at TEXT,
                graded_by TEXT,
                FOREIGN KEY (assignment_id) REFERENCES assignments(id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== 学生管理 ==========
    
    def add_student(self, student_data: dict) -> bool:
        """添加学生"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (
                    student_id, name, union_id, level, status,
                    contact_channel, contact_address,
                    public_key, encrypted_private_key,
                    badge_png, badge_svg,
                    enrolled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_data["student_id"],
                student_data["name"],
                student_data["union_id"],
                student_data.get("level", "L1"),
                student_data.get("status", "在读"),
                student_data.get("contact_channel"),
                student_data.get("contact_address"),
                student_data.get("public_key"),
                student_data.get("encrypted_private_key"),
                student_data.get("badge_png"),
                student_data.get("badge_svg"),
                student_data.get("enrolled_at", datetime.now().isoformat())
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"添加学生失败：{e}")
            return False
        finally:
            conn.close()
    
    def get_student(self, student_id: str) -> Optional[dict]:
        """获取学生信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_students(self, level: str = None, status: str = None) -> List[dict]:
        """列出学生（可过滤）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM students WHERE 1=1'
        params = []
        
        if level:
            query += ' AND level = ?'
            params.append(level)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY enrolled_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_student(self, student_id: str, updates: dict) -> bool:
        """更新学生信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        if not set_clauses:
            conn.close()
            return False
        
        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(student_id)
        
        query = f"UPDATE students SET {', '.join(set_clauses)} WHERE student_id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def graduate_student(self, student_id: str, final_level: str) -> bool:
        """毕业学生"""
        return self.update_student(student_id, {
            "status": "毕业",
            "level": final_level,
            "graduated_at": datetime.now().isoformat()
        })
    
    def delete_student(self, student_id: str) -> bool:
        """
        删除学生及相关数据
        
        Args:
            student_id: 学号
            
        Returns:
            是否删除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 删除学术记录
            cursor.execute('DELETE FROM academic_records WHERE student_id = ?', (student_id,))
            
            # 删除贡献记录
            cursor.execute('DELETE FROM contributions WHERE student_id = ?', (student_id,))
            
            # 删除荣誉记录
            cursor.execute('DELETE FROM honors WHERE student_id = ?', (student_id,))
            
            # 删除消息（发送和接收的）
            cursor.execute('DELETE FROM messages WHERE to_id = ? OR from_id = ?', (student_id, student_id))
            
            # 删除作业提交
            cursor.execute('DELETE FROM submissions WHERE student_id = ?', (student_id,))
            
            # 删除学生基本信息
            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"删除学生失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # ========== 学术记录 ==========
    
    def add_academic_record(self, student_id: str, record_type: str, 
                           record_data: dict, signature: str = None) -> bool:
        """添加学术记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO academic_records (student_id, record_type, record_data, timestamp, signature)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            student_id,
            record_type,
            json.dumps(record_data, ensure_ascii=False),
            datetime.now().isoformat(),
            signature
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_academic_records(self, student_id: str) -> List[dict]:
        """获取学生学术记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM academic_records WHERE student_id = ? ORDER BY timestamp',
            (student_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            d = dict(row)
            d["record_data"] = json.loads(d["record_data"])
            results.append(d)
        
        return results
    
    # ========== 消息队列 ==========
    
    def add_message(self, message_data: dict) -> bool:
        """添加消息到队列"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (
                id, from_id, to_id, encrypted_content, nonce, tag,
                encrypted_aes_key, sender_signature, msg_type, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_data["id"],
            message_data["from_id"],
            message_data["to_id"],
            message_data["encrypted_content"],
            message_data.get("nonce", ""),
            message_data.get("tag", ""),
            message_data.get("encrypted_aes_key"),
            message_data.get("sender_signature"),
            message_data.get("msg_type", "text"),
            message_data.get("status", "pending"),
            message_data.get("created_at", datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_messages(self, student_id: str, status: str = "pending", 
                    limit: int = 100) -> List[dict]:
        """获取学生消息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM messages 
            WHERE to_id = ? AND status = ?
            ORDER BY created_at DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (student_id, status, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def mark_message_read(self, message_id: str) -> bool:
        """标记消息为已读"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages 
            SET status = 'read', read_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), message_id))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    # ========== 统计 ==========
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 学生统计
        cursor.execute('SELECT COUNT(*) as count FROM students')
        stats["total_students"] = cursor.fetchone()["count"]
        
        cursor.execute('SELECT COUNT(*) as count FROM students WHERE status = ?', ('在读',))
        stats["active_students"] = cursor.fetchone()["count"]
        
        # 消息统计
        cursor.execute('SELECT COUNT(*) as count FROM messages WHERE status = ?', ('pending',))
        stats["pending_messages"] = cursor.fetchone()["count"]
        
        conn.close()
        
        return stats


# 测试
if __name__ == "__main__":
    db = Database(data_dir="./data")
    
    print("=== SQLite 数据库测试 ===\n")
    
    # 添加测试学生
    student = {
        "student_id": "S_20260321_001",
        "name": "小虾米",
        "union_id": "on_S_20260321_001",
        "level": "L1",
        "contact_channel": "feishu",
        "contact_address": "on_test123",
        "public_key": "TEST_PUBLIC_KEY",
        "encrypted_private_key": "TEST_ENCRYPTED_KEY",
        "badge_png": "badges/S_20260321_001.png",
        "badge_svg": "badges/S_20260321_001.svg"
    }
    
    print("1. 添加学生...")
    db.add_student(student)
    
    # 查询学生
    print("2. 查询学生...")
    s = db.get_student("S_20260321_001")
    print(f"   姓名：{s['name']}")
    print(f"   学号：{s['student_id']}")
    
    # 列出学生
    print("3. 列出所有学生...")
    students = db.list_students()
    for s in students:
        print(f"   - {s['name']} ({s['student_id']})")
    
    # 统计
    print("4. 统计信息...")
    stats = db.get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")
