#!/usr/bin/env python3
"""
学思通 - 飞书通知插件

注意：此插件需要在 OpenClaw 环境中运行，
通过 sessions_send 工具发送飞书消息。
"""

from .base import NotificationPlugin


class FeishuPlugin(NotificationPlugin):
    """飞书通知插件"""
    
    @property
    def name(self) -> str:
        return "feishu"
    
    def send(self, recipient: str, message: str) -> bool:
        """
        通过飞书发送通知
        
        Args:
            recipient: 接收者 Union ID（格式：on_S_20260321_001）
            message: 消息内容
            
        Returns:
            bool: 是否发送成功
            
        注意：此方法在 OpenClaw 环境中会被增强，
        实际调用 sessions_send 工具发送消息。
        """
        try:
            # Union ID 转 session key
            # on_S_20260321_001 → agent:main:feishu:direct:on_S_20260321_001
            session_key = f"agent:main:feishu:direct:{recipient}"
            
            # 在 OpenClaw 环境中，这里会调用 sessions_send 工具
            # 由于这是插件代码，实际调用由主模块处理
            print(f"📨 准备发送飞书消息：{recipient}")
            print(f"   Session: {session_key}")
            print(f"   消息：{message[:50]}...")
            
            # TODO: 在 OpenClaw 主程序中调用 sessions_send
            # sessions_send(sessionKey=session_key, message=message)
            
            return True
            
        except Exception as e:
            print(f"❌ 飞书消息发送失败：{e}")
            return False
    
    def verify(self, contact_address: str) -> bool:
        """
        验证飞书 Union ID 格式
        
        Args:
            contact_address: 飞书 Union ID
            
        Returns:
            bool: 格式是否有效
        """
        # Union ID 格式：on_xxx
        if not contact_address:
            return False
        
        return contact_address.startswith("on_")
    
    def __str__(self) -> str:
        return f"FeishuPlugin()"
