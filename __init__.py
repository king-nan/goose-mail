# 鸿雁 / GooseMail - 智慧大脑学院通讯系统
# 代号：学思通 (XueSitong)
# Slogan：鸿雁传书，学思无阻

__version__ = "0.1.0"
__author__ = "澜宝 & 智虾"

from .core.student_id import StudentIDGenerator
from .core.keys import KeyManager
from .core.crypto import CryptoManager
from .core.audit import AuditLogger
from .storage.database import Database

__all__ = [
    "StudentIDGenerator",
    "KeyManager",
    "CryptoManager",
    "AuditLogger",
    "Database",
]
