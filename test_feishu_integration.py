#!/usr/bin/env python3
"""
学思通 - 飞书插件集成测试

用法：
    python3 test_feishu_integration.py
"""

import sys
sys.path.insert(0, '/home/gem/workspace/agent/skills/学思通')

from xuesitong import XueSitong
from plugins.feishu import FeishuPlugin


def main():
    print("=" * 60)
    print("学思通 - 飞书插件集成测试")
    print("=" * 60)
    
    # 初始化学思通
    xs = XueSitong(data_dir="./data")
    
    # 注册飞书插件
    feishu = FeishuPlugin()
    xs.register_plugin(feishu)
    print(f"✅ 飞书插件已注册：{feishu.name}")
    
    # 测试学员注册
    print("\n" + "-" * 60)
    print("测试 1: 学员入学")
    print("-" * 60)
    
    test_students = [
        {"name": "智虾", "level": "L1", "union_id": "ou_0fc552ac343ffb7fc45e560d2f7201a5"},
        {"name": "澜宝", "level": "L2", "union_id": "on_528e3973b54c5118088a0f5391726c1a"},
        {"name": "小虾米", "level": "L1", "union_id": "on_9283dca44042d98848b4efbc599d2209"},
    ]
    
    for student in test_students:
        result = xs.enroll(
            name=student["name"],
            level=student["level"],
            union_id=student["union_id"],
            contact_channel="feishu",
            contact_address=student["union_id"]
        )
        print(f"✅ {student['name']} 已入学")
        print(f"   学号：{result['student_id']}")
        print(f"   二维码：{result['badge_path']}")
    
    # 测试消息发送
    print("\n" + "-" * 60)
    print("测试 2: 发送通知")
    print("-" * 60)
    
    # 获取学员列表
    students = xs.list_students()
    print(f"📋 当前学员数：{len(students)}")
    
    for student in students:
        student_id = student["student_id"]
        union_id = student["union_id"]
        
        # 发送测试消息
        message = f"""
🦐 智慧大脑学院 - 测试通知

亲爱的 {student['name']}：

欢迎加入智慧大脑学院！

📚 你的学号：{student_id}
🎓 当前等级：{student['level']}
📅 入学时间：{student['enrolled_at']}

学思通系统测试中...
        """
        
        # 通过飞书发送
        xs.send_notification(
            student_id=student_id,
            message=message.strip()
        )
    
    # 显示统计
    print("\n" + "-" * 60)
    print("测试 3: 系统统计")
    print("-" * 60)
    
    stats = xs.get_stats()
    print(f"📊 学生总数：{stats['total_students']}")
    print(f"📊 在读学生：{stats['active_students']}")
    print(f"📊 待读消息：{stats['pending_messages']}")
    print(f"📊 审计日志：{stats['audit_entries']} 条")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
