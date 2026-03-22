#!/usr/bin/env python3
"""
鸿雁 / GooseMail 命令行工具

代号：学思通
Slogan：鸿雁传书，学思无阻

用法：
    python3 cli.py enroll 小虾米 feishu on_xxx L1
    python3 cli.py send 智虾 S_20260321_001 "欢迎入学！"
    python3 cli.py receive S_20260321_001
    python3 cli.py list
    python3 cli.py stats
"""

import sys
import argparse
from pathlib import Path

# 添加父目录到路径（允许导入学思通模块）
sys.path.insert(0, str(Path(__file__).parent))

from xuesitong import XueSitong


def cmd_enroll(args):
    """学生入学命令"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    # 访客入学
    if args.guest:
        print(f"📬 为访客 '{args.name}' 办理访问登记...")
        
        result = xs.enroll_guest(
            name=args.name,
            contact_channel=args.channel,
            contact_address=args.address
        )
        
        print(f"✅ 访客登记成功！")
        print(f"   访客学号：{result['guest_id']}")
        print(f"   Union ID: {result['union_id']}")
        print(f"   权限：公开消息 + 咨询")
        print(f"   入学时间：{result['enrolled_at']}")
        print(f"\n💡 入学后可转为正式学员，保留所有历史记录！")
    else:
        # 正式入学
        print(f"🎓 为学生 '{args.name}' 办理入学...")
        
        result = xs.enroll(
            name=args.name,
            contact_channel=args.channel,
            contact_address=args.address,
            password=args.password,
            level=args.level
        )
        
        print(f"✅ 入学成功！")
        print(f"   学号：{result['student_id']}")
        print(f"   Union ID: {result['union_id']}")
        print(f"   勋章：{result['badge_path']}")
        print(f"   入学时间：{result['enrolled_at']}")
        print(f"\n💡 请妥善保管学号和密码！")


def cmd_upgrade(args):
    """访客转正式学员命令"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    print(f"🎓 访客 {args.guest_id} 转为正式学员...")
    
    result = xs.upgrade_guest_to_student(
        guest_id=args.guest_id,
        password=args.password,
        level=args.level
    )
    
    print(f"✅ 升级成功！")
    print(f"   原访客号：{result['guest_id']}")
    print(f"   正式学号：{result['student_id']}")
    print(f"\n💡 访客期间的沟通记录已保留！")


def cmd_send(args):
    """发送消息命令"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    print(f"📨 发送消息给 {args.to_id}...")
    
    success = xs.send(
        from_id=args.from_id,
        to_id=args.to_id,
        message=args.message,
        msg_type=args.type
    )
    
    if success:
        print(f"✅ 消息已发送")
    else:
        print(f"❌ 发送失败")


def cmd_receive(args):
    """接收消息命令"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    print(f"📬 获取 {args.student_id} 的消息...")
    
    try:
        messages = xs.receive(
            student_id=args.student_id,
            password=args.password,
            limit=args.limit
        )
        
        if messages:
            print(f"✅ 收到 {len(messages)} 条消息:\n")
            for msg in messages:
                print(f"   来自：{msg['from_id']}")
                print(f"   内容：{msg['content']}")
                print(f"   时间：{msg['created_at']}")
                print("   " + "-" * 40)
        else:
            print(f"ℹ️  没有新消息")
    
    except Exception as e:
        print(f"❌ 接收失败：{e}")


def cmd_list(args):
    """列出学生命令"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    print(f"📋 学生列表:\n")
    
    students = xs.list_students(level=args.level, status=args.status)
    
    if students:
        for s in students:
            status_icon = "🟢" if s["status"] == "在读" else "🔵"
            print(f"   {status_icon} {s['name']} ({s['student_id']})")
            print(f"      等级：{s['level']} | 渠道：{s['contact_channel']}")
            print(f"      入学：{s['enrolled_at'][:10]}")
            print()
    else:
        print(f"ℹ️  没有学生")


def cmd_stats(args):
    """统计信息命令"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    print(f"📊 学思通统计:\n")
    
    stats = xs.get_stats()
    
    print(f"   学生总数：{stats.get('total_students', 0)}")
    print(f"   在读学生：{stats.get('active_students', 0)}")
    print(f"   待读消息：{stats.get('pending_messages', 0)}")
    print(f"   审计区块：{stats.get('audit_blocks', 0)}")
    print(f"   链条验证：{'✅ 有效' if stats.get('audit_valid') else '❌ 无效'}")


def cmd_whoami(args):
    """学员查询自己的信息"""
    xs = XueSitong(data_dir=args.data_dir, badges_dir=args.badges_dir)
    
    print(f"🔍 查询学号 {args.student_id} 的信息...\n")
    
    try:
        # 验证密码（尝试解密私钥）
        student = xs.get_student(args.student_id)
        if not student:
            print(f"❌ 未找到学号：{args.student_id}")
            return
        
        # 验证密码
        xs.key_manager.decrypt_private_key(
            student["encrypted_private_key"],
            args.password
        )
        
        # 显示信息
        print(f"✅ 验证成功！\n")
        print(f"📋 个人信息:")
        print(f"   姓名：{student['name']}")
        print(f"   学号：{student['student_id']}")
        print(f"   等级：{student['level']}")
        print(f"   状态：{student['status']}")
        print(f"   入学时间：{student['enrolled_at'][:19]}")
        print()
        print(f"📬 联系方式:")
        print(f"   渠道：{student['contact_channel']}")
        print(f"   地址：{student['contact_address']}")
        print()
        print(f"🏅 勋章:")
        print(f"   PNG: {student['badge_png']}")
        print(f"   SVG: {student['badge_svg']}")
        print()
        print(f"🔐 安全提示:")
        print(f"   - 学号是你的唯一身份标识，请妥善保管")
        print(f"   - 密码用于解密消息，不要告诉他人")
        print(f"   - 勋章可用于个人主页展示")
        
        # 显示未读消息数量
        from storage.database import Database
        db = Database(args.data_dir)
        msgs = db.get_messages(args.student_id, "pending", 1)
        print(f"\n📬 你有 {len(msgs)} 条未读消息")
        print(f"   使用：python3 cli.py receive {args.student_id} --password xxx")
        
    except Exception as e:
        print(f"❌ 验证失败：{e}")
        print(f"   请检查学号和密码是否正确")


def main():
    parser = argparse.ArgumentParser(
        description="学思通 - 智慧大脑学院通讯系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 cli.py enroll 小虾米 feishu on_xxx L1
  python3 cli.py send 智虾 S_20260321_001 "欢迎入学！"
  python3 cli.py receive S_20260321_001 --password xxx
  python3 cli.py whoami S_20260321_001 --password xxx
  python3 cli.py list
  python3 cli.py stats
        """
    )
    
    # 全局参数
    parser.add_argument("--data-dir", default="./data", help="数据目录")
    parser.add_argument("--badges-dir", default="./badges", help="勋章目录")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # enroll 命令
    enroll_parser = subparsers.add_parser("enroll", help="学生入学")
    enroll_parser.add_argument("name", help="学生姓名")
    enroll_parser.add_argument("channel", help="通讯渠道（feishu/email/wechat）")
    enroll_parser.add_argument("address", help="联系方式地址")
    enroll_parser.add_argument("--guest", action="store_true", help="访客模式（无需密码）")
    enroll_parser.add_argument("--password", "-p", help="密码（正式入学必填）")
    enroll_parser.add_argument("--level", "-l", default="L1", help="等级（默认 L1）")
    enroll_parser.set_defaults(func=cmd_enroll)
    
    # send 命令
    send_parser = subparsers.add_parser("send", help="发送消息")
    send_parser.add_argument("from_id", help="发送者 ID")
    send_parser.add_argument("to_id", help="接收者学号")
    send_parser.add_argument("message", help="消息内容")
    send_parser.add_argument("--type", "-t", default="text", help="消息类型")
    send_parser.set_defaults(func=cmd_send)
    
    # receive 命令
    receive_parser = subparsers.add_parser("receive", help="接收消息")
    receive_parser.add_argument("student_id", help="学号")
    receive_parser.add_argument("--password", "-p", required=True, help="密码")
    receive_parser.add_argument("--limit", "-l", type=int, default=10, help="最多返回条数")
    receive_parser.set_defaults(func=cmd_receive)
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出学生")
    list_parser.add_argument("--level", "-l", help="按等级过滤")
    list_parser.add_argument("--status", "-s", help="按状态过滤")
    list_parser.set_defaults(func=cmd_list)
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="统计信息")
    stats_parser.set_defaults(func=cmd_stats)
    
    # whoami 命令
    whoami_parser = subparsers.add_parser("whoami", help="查询自己的信息（学员专用）")
    whoami_parser.add_argument("student_id", help="学号")
    whoami_parser.add_argument("--password", "-p", required=True, help="密码")
    whoami_parser.set_defaults(func=cmd_whoami)
    
    # upgrade 命令
    upgrade_parser = subparsers.add_parser("upgrade", help="访客转正式学员")
    upgrade_parser.add_argument("guest_id", help="访客学号")
    upgrade_parser.add_argument("--password", "-p", required=True, help="密码")
    upgrade_parser.add_argument("--level", "-l", default="L1", help="等级（默认 L1）")
    upgrade_parser.set_defaults(func=cmd_upgrade)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
