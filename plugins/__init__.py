#!/usr/bin/env python3
"""
学思通 - 通知插件包
"""

from .base import NotificationPlugin
from .feishu import FeishuPlugin

__all__ = ["NotificationPlugin", "FeishuPlugin"]
