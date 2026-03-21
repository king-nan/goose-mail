# 鸿雁 / GooseMail

> **智慧大脑学院专用通讯系统**  
> **版本**：0.1.0 (MVP)  
> **作者**：澜宝 & 智虾  
> **创建时间**：2026-03-21

---

## 🪿 简介

**鸿雁**（GooseMail），代号"学思通"，是智慧大脑学院的专用通讯系统。

> **Slogan**：鸿雁传书，学思无阻

为每位学员提供：
- 🎓 **终身学号** - 格式 `S_YYYYMMDD_序号`，终身唯一
- 🔐 **安全加密** - AES-256 + RSA-2048 端到端加密
- 🏅 **二维码勋章** - 入学即获唯一身份标识
- 📜 **永久档案** - SQLite + 区块链式审计日志
- 🔌 **多平台支持** - 飞书/邮件/微信/Web（插件化）

---

## 📖 名字由来

**鸿雁**出自中国典故"鸿雁传书"，寓意：
- 🪿 **传递知识** - 如鸿雁传递家书，我们传递知识
- 📬 **安全可靠** - 鸿雁南飞，千里不误
- 🔗 **连接师生** - 连接学院与每位学员
- 🎓 **学思无阻** - 让学习之路畅通无阻

**学思通**作为技术代号，取自《论语》"学而不思则罔，思而不学则殆"。

---

## 🚀 快速开始

### 安装依赖

```bash
cd /home/gem/workspace/agent/skills/学思通
pip3 install -r requirements.txt
```

### 学生入学

```bash
# 命令行
python3 cli.py enroll 小虾米 feishu on_xxx --password 123456 --level L1

# Python 代码
from xuesitong import XueSitong

xs = XueSitong()
result = xs.enroll(
    name="小虾米",
    contact_channel="feishu",
    contact_address="on_xxx",
    password="123456",
    level="L1"
)

print(f"学号：{result['student_id']}")
print(f"勋章：{result['badge_path']}")
```

### 发送消息

```bash
# 命令行
python3 cli.py send 智虾 S_20260321_001 "欢迎入学！"

# Python 代码
xs.send("智虾", "S_20260321_001", "欢迎入学！")
```

### 接收消息

```bash
# 命令行
python3 cli.py receive S_20260321_001 --password 123456

# Python 代码
messages = xs.receive("S_20260321_001", password="123456")
for msg in messages:
    print(f"来自 {msg['from_id']}: {msg['content']}")
```

---

## 💻 命令行工具

### 所有命令

```bash
# 学生入学
python3 cli.py enroll <姓名> <渠道> <地址> --password <密码> [--level L1]

# 发送消息
python3 cli.py send <发送者> <学号> <消息内容>

# 接收消息
python3 cli.py receive <学号> --password <密码>

# 列出学生
python3 cli.py list [--level L1] [--status 在读]

# 统计信息
python3 cli.py stats

# 查看帮助
python3 cli.py --help
```

---

## 📋 API 参考

### XueSitong 类

#### 初始化
```python
xs = XueSitong(data_dir="./data", badges_dir="./badges")
```

#### enroll() - 学生入学
```python
result = xs.enroll(
    name="小虾米",
    contact_channel="feishu",  # feishu/email/wechat/telegram/web
    contact_address="on_xxx",
    password="secure_password",
    level="L1"
)
# 返回：{student_id, union_id, badge_path, public_key, enrolled_at}
```

#### send() - 发送消息
```python
xs.send(
    from_id="智虾",
    to_id="S_20260321_001",
    message="欢迎入学！",
    msg_type="text"  # text/markdown
)
```

#### receive() - 接收消息
```python
messages = xs.receive(
    student_id="S_20260321_001",
    password="secure_password",
    limit=10
)
```

#### get_student() - 查询学生
```python
student = xs.get_student("S_20260321_001")
```

#### list_students() - 列出学生
```python
students = xs.list_students(level="L1", status="在读")
```

#### get_stats() - 统计信息
```python
stats = xs.get_stats()
# 返回：total_students, active_students, pending_messages, audit_blocks, audit_valid
```

---

## 🔐 安全设计

### 加密方案
- **消息加密**：AES-256-GCM
- **密钥交换**：RSA-2048 OAEP
- **数字签名**：RSA-PKCS1v15 + SHA256
- **私钥保护**：PBKDF2（100000 轮）+ AES-256

### 审计日志
- **区块链式结构**：每块包含前一块哈希
- **不可篡改**：修改任意块会破坏后续所有块
- **完整追溯**：记录所有关键操作

---

## 📁 目录结构

```
学思通/
├── __init__.py
├── xuesitong.py           # 主模块
├── cli.py                 # 命令行工具
├── requirements.txt       # Python 依赖
├── SKILL.md              # 本文档
│
├── core/                 # 核心模块
│   ├── student_id.py     # 学号生成
│   ├── keys.py           # 密钥管理
│   ├── crypto.py         # 加密/签名
│   ├── audit.py          # 审计日志
│   └── badge.py          # 勋章生成
│
├── storage/              # 存储模块
│   └── database.py       # SQLite 数据库
│
├── plugins/              # 通讯插件（可选）
│   ├── base.py           # 插件基类
│   └── feishu.py         # 飞书插件（待实现）
│
├── data/                 # 数据目录（运行时创建）
│   ├── students.db       # SQLite 数据库
│   ├── audit.jsonl       # 审计日志
│   └── student_counter.json
│
└── badges/               # 勋章目录（运行时创建）
    └── S_YYYYMMDD_序号.png
```

---

## 🎓 使用场景

### 1. 学员入学
```python
# 批量入学
students = [
    ("小虾米", "feishu", "on_xxx1", "L1"),
    ("澜宝", "feishu", "on_xxx2", "L1"),
    ("智虾", "email", "zhixia@example.com", "L1"),
]

for name, channel, address, level in students:
    xs.enroll(name, channel, address, "password123", level)
```

### 2. 开课通知
```python
# 通知所有 L1 学员
l1_students = xs.list_students(level="L1")
for student in l1_students:
    xs.send("教务处", student["student_id"], 
            "下周一 L1 课程开课，请准时参加！")
```

### 3. 作业提醒
```python
# 提醒未完成作业的学员
pending = get_pending_assignments()  # 自定义函数
for student_id in pending:
    xs.send("助教", student_id, "作业即将到期，请抓紧提交！")
```

### 4. 毕业通知
```python
# 毕业学员
xs.send("院长", "S_20260321_001", 
        "恭喜你完成所有课程，正式毕业！")
xs.db.graduate_student("S_20260321_001", "L4")
```

---

## 🔌 插件开发

### 插件基类
```python
# plugins/base.py
from abc import ABC, abstractmethod

class NotificationPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass
```

### 飞书插件示例
```python
# plugins/feishu.py
from .base import NotificationPlugin
from sessions_send import send_message

class FeishuPlugin(NotificationPlugin):
    @property
    def name(self) -> str:
        return "feishu"
    
    def send(self, recipient: str, message: str) -> bool:
        # recipient 格式：on_xxx
        session_key = f"agent:main:feishu:direct:{recipient}"
        send_message(sessionKey=session_key, message=message)
        return True

# 注册插件
xs = XueSitong()
xs.register_plugin(FeishuPlugin())
```

---

## 🧪 测试

```bash
cd /home/gem/workspace/agent/skills/学思通

# 运行测试
python3 xuesitong.py

# 或手动测试
python3 cli.py enroll 测试用户 feishu on_test --password 123
python3 cli.py send 智虾 S_20260321_001 "你好！"
python3 cli.py list
python3 cli.py stats
```

---

## 📊 数据结构

### 学生信息
```json
{
  "student_id": "S_20260321_001",
  "name": "小虾米",
  "union_id": "on_S_20260321_001",
  "level": "L1",
  "status": "在读",
  "contact_channel": "feishu",
  "contact_address": "on_xxx",
  "public_key": "RSA_PUBLIC_KEY",
  "encrypted_private_key": "AES_ENCRYPTED",
  "badge_png": "badges/S_20260321_001.png",
  "enrolled_at": "2026-03-21T19:00:00"
}
```

### 审计日志
```json
{
  "seq": 1,
  "prev_hash": "0",
  "action": "student_enroll",
  "actor": "system",
  "target": "S_20260321_001",
  "data_hash": "abc123...",
  "signature": "system",
  "timestamp": "2026-03-21T19:00:00",
  "hash": "def456..."
}
```

---

## 🚧 待完善功能

### MVP 之后
- [ ] 飞书插件完整实现
- [ ] 邮件插件
- [ ] Web 界面
- [ ] 消息完整解密流程
- [ ] 批量导入学生
- [ ] 课程和作业管理
- [ ] 学习进度追踪

### 长期规划
- [ ] 微信插件
- [ ] Telegram 插件
- [ ] 自动化提醒
- [ ] 数据备份
- [ ] 多实例同步

---

## 📝 最佳实践

### 1. 密码安全
- 至少 8 位，包含字母 + 数字
- 不要明文存储或传输
- 定期提醒学生修改

### 2. 学号管理
- 学号终身唯一，不要重复使用
- 妥善保管学号计数器文件

### 3. 审计日志
- 定期检查链条完整性
- 不要手动修改审计文件

### 4. 数据备份
- 定期备份 data/ 目录
- 重要操作前手动备份

---

## 📖 相关文档

- [智慧大脑学院规划](../../../workspace/memory/智慧大脑学院.md)
- [agent-comms 技能](../agent-comms/SKILL.md)
- [飞书集成技能](../../openclaw-lark/skills/feishu-im-user-message/SKILL.md)

---

**Made with ❤️ for 智慧大脑学院**

*让每只虾米找到方向* 🦐
