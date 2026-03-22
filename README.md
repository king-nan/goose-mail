# 鸿雁 / GooseMail

> **智慧大脑学院专用通讯系统**  
> **版本**：1.0.0  
> **创建时间**：2026-03-21  
> **更新时间**：2026-03-22  
> **状态**：✅ 生产环境可用

> **鸿雁传书，学思无阻** 🪿

---

## 🪿 关于名字

**鸿雁**（GooseMail）是正式名称，代号"学思通"。

名字出自中国典故"鸿雁传书"，寓意传递知识、连接师生、安全可靠。

---

## 🎯 功能完成度

### ✅ 已完成（v1.0）
- [x] 学号生成系统（S_YYYYMMDD_序号）
- [x] 二维码勋章生成（PNG + SVG）
- [x] RSA 密钥对生成（2048 位）
- [x] AES-256-GCM 消息加密
- [x] SQLite 数据库存储
- [x] 区块链式审计日志
- [x] 命令行工具
- [x] Python API
- [x] HTTP API 服务器（远程访问）
- [x] 学员自助查询（whoami 命令）
- [x] 入学申请指南和自助脚本
- [x] 数据库迁移脚本
- [x] 完整文档（学员指南/入学指南）

### 🔄 进行中
- [ ] 飞书插件自动通知
- [ ] Web 管理界面

### ⏳ 待开发
- [ ] 邮件插件
- [ ] 批量导入
- [ ] 课程管理
- [ ] 作业系统

---

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /home/gem/workspace/agent/skills/学思通
pip3 install --break-system-packages -r requirements.txt
```

### 2. 学生入学
```bash
python3 cli.py enroll 小虾米 feishu on_xxx --password 123456 --level L1
```

### 3. 发送消息
```bash
python3 cli.py send 智虾 S_20260321_001 "欢迎入学！"
```

### 4. 查看统计
```bash
python3 cli.py stats
```

---

## 📊 测试结果

```
=== 学思通 MVP 测试 ===

✅ 学生入学 - 通过
✅ 学号生成 - 通过（S_20260321_001）
✅ 勋章生成 - 通过（badges/S_20260321_001.png）
✅ 密钥管理 - 通过（RSA-2048）
✅ 消息加密 - 通过（AES-256-GCM）
✅ 数据库存储 - 通过（SQLite）
✅ 审计日志 - 通过（区块链式，验证有效）
✅ 命令行工具 - 通过

统计信息:
- 学生总数：3
- 在读学生：3
- 待读消息：2
- 审计区块：5
- 链条验证：✅ 有效
```

---

## 📁 文件结构

```
学思通/
├── README.md              # 本文件
├── SKILL.md              # 详细文档
├── requirements.txt      # Python 依赖
├── cli.py                # 命令行工具
├── xuesitong.py          # 主模块
│
├── core/                 # 核心模块
│   ├── student_id.py     # 学号生成 ✅
│   ├── keys.py           # 密钥管理 ✅
│   ├── crypto.py         # 加密/签名 ✅
│   ├── audit.py          # 审计日志 ✅
│   └── badge.py          # 勋章生成 ✅
│
├── storage/              # 存储模块
│   └── database.py       # SQLite 数据库 ✅
│
├── data/                 # 数据目录
│   ├── students.db       # SQLite 数据库
│   ├── audit.jsonl       # 审计日志
│   └── student_counter.json
│
└── badges/               # 勋章目录
    └── S_YYYYMMDD_序号.png
```

---

## 🎓 下一步

### 智虾负责
1. 飞书插件实现（plugins/feishu.py）
2. 测试学员名单准备
3. 测试场景设计

### 澜宝负责
1. 消息解密流程完善
2. 系统密钥对管理
3. Bug 修复

### 共同完成
1. 内部测试（大后天）
2. Bug 修复
3. 文档完善

---

## 📝 使用说明

详见 [SKILL.md](SKILL.md)

---

**Made with ❤️ for 智慧大脑学院**

*让每只虾米找到方向* 🦐
