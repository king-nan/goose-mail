#!/usr/bin/env python3
"""
学思通 - 通知插件基类
"""

from abc import ABC, abstractmethod


class NotificationPlugin(ABC):
    """通知插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """
        发送通知
        
        Args:
            recipient: 接收者（学号或 Union ID）
            message: 消息内容
            
        Returns:
            bool: 是否发送成功
        """
        pass
    
    @abstractmethod
    def verify(self, contact_address: str) -> bool:
        """
        验证联系方式格式
        
        Args:
            contact_address: 联系方式（飞书 ID/邮箱/等）
            
        Returns:
            bool: 格式是否有效
        """
        pass
    
    def __str__(self) -> str:
        return f"NotificationPlugin({self.name})"
