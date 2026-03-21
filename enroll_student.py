#!/usr/bin/env python3
"""
鸿雁入学申请脚本

为学员提供交互式的入学申请流程。

用法：
    python3 enroll_student.py
"""

import sys
import getpass
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from xuesitong import XueSitong


def get_input(prompt, default=None, required=True):
    """获取用户输入"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        value = input(prompt).strip()
        if not value and default:
            return default
        if not value and required:
            print("   ❌ 此项必填，请重新输入")
            continue
        return value


def get_password():
    """安全获取密码"""
    print("\n🔐 设置密码")
    print("   要求：至少 8 位，包含字母 + 数字")
    print("   ⚠️  密码用于解密消息，不要告诉他人\n")
    
    while True:
        password = getpass.getpass("   密码：")
        if len(password) < 8:
            print("   ❌ 密码长度至少 8 位")
            continue
        
        password_confirm = getpass.getpass("   确认密码：")
        if password != password_confirm:
            print("   ❌ 两次输入的密码不一致")
            continue
        
        # 简单检查是否包含字母和数字
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_letter and has_digit):
            print("   ❌ 密码必须包含字母和数字")
            continue
        
        return password


def main():
    """主函数"""
    print("=" * 60)
    print("🎓 智慧大脑学院 - 入学申请")
    print("=" * 60)
    print()
    print("欢迎加入智慧大脑学院！")
    print("请填写以下信息完成入学申请\n")
    
    # 收集信息
    print("📋 基本信息")
    name = get_input("姓名/昵称", required=True)
    
    print("\n📬 联系方式")
    print("   支持的渠道：feishu / email / wechat / telegram")
    channel = get_input("   通讯渠道", default="feishu")
    address = get_input(f"   {channel} ID/地址", required=True)
    
    print("\n🎯 学习信息")
    print("   等级说明：")
    print("   - L1: 入门（AI Agent 基础）")
    print("   - L2: 进阶（技能开发）")
    print("   - L3: 高级（系统集成）")
    print("   - L4: 专家（独立项目）")
    level = get_input("   初始等级", default="L1")
    
    # 获取密码
    password = get_password()
    
    # 确认信息
    print("\n" + "=" * 60)
    print("📝 请确认以下信息：")
    print("=" * 60)
    print(f"   姓名：{name}")
    print(f"   联系方式：{channel} - {address}")
    print(f"   等级：{level}")
    print()
    
    confirm = input("确认入学？(y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ 已取消入学申请")
        return
    
    # 执行入学
    print("\n🎓 正在办理入学...")
    
    try:
        xs = XueSitong(data_dir="./data", badges_dir="./badges")
        
        result = xs.enroll(
            name=name,
            contact_channel=channel,
            contact_address=address,
            password=password,
            level=level
        )
        
        print("\n" + "=" * 60)
        print("✅ 入学成功！")
        print("=" * 60)
        print(f"\n🎓 你的学号：{result['student_id']}")
        print(f"🏅 勋章路径：{result['badge_path']}")
        print(f"📅 入学时间：{result['enrolled_at'][:19]}")
        
        print("\n🔐 重要提示：")
        print(f"   1. 请妥善保管学号：{result['student_id']}")
        print("   2. 密码已设置，不要告诉他人")
        print("   3. 使用 whoami 命令可随时查询自己的信息")
        
        print("\n📚 下一步：")
        print(f"   1. 查询信息：python3 cli.py whoami {result['student_id']} --password <密码>")
        print(f"   2. 查看消息：python3 cli.py receive {result['student_id']} --password <密码>")
        print("   3. 阅读学员指南：cat 学员指南.md")
        
        print("\n" + "=" * 60)
        print("🪿 鸿雁传书，学思无阻")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 入学失败：{e}")
        print("   请联系管理员寻求帮助")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 已中断入学申请")
        sys.exit(0)
