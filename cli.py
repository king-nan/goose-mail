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


def main():
    parser = argparse.ArgumentParser(
        description="学思通 - 智慧大脑学院通讯系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 cli.py enroll 小虾米 feishu on_xxx L1
  python3 cli.py send 智虾 S_20260321_001 "欢迎入学！"
  python3 cli.py receive S_20260321_001 --password xxx
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
    enroll_parser.add_argument("--password", "-p", required=True, help="密码")
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
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
