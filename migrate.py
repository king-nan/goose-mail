#!/usr/bin/env python3
"""
鸿雁数据库迁移脚本

用法：
    python3 migrate.py
"""

import sqlite3
from pathlib import Path

def migrate(data_dir: str = "./data"):
    """执行数据库迁移"""
    db_path = Path(data_dir) / "students.db"
    
    if not db_path.exists():
        print(f"❌ 数据库不存在：{db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("=== 鸿雁数据库迁移 ===\n")
    
    # 检查是否需要迁移
    cursor.execute('PRAGMA table_info(messages)')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'nonce' in columns and 'tag' in columns:
        print("✅ 数据库已是最新版本")
    else:
        print("📝 执行迁移...")
        
        # 添加 nonce 字段
        if 'nonce' not in columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN nonce TEXT DEFAULT ""')
            print("   ✅ 添加 nonce 字段")
        
        # 添加 tag 字段
        if 'tag' not in columns:
            cursor.execute('ALTER TABLE messages ADD COLUMN tag TEXT DEFAULT ""')
            print("   ✅ 添加 tag 字段")
        
        conn.commit()
        print("\n✅ 迁移完成！")
    
    # 验证结构
    cursor.execute('PRAGMA table_info(messages)')
    print("\n📋 messages 表结构:")
    for col in cursor.fetchall():
        print(f"   {col[1]}: {col[2]}")
    
    conn.close()


if __name__ == "__main__":
    import sys
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    migrate(data_dir)
