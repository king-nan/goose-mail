"""
密钥管理器

功能：
- 生成 RSA 密钥对（2048 位）
- 加密/解密私钥（使用学生密码）
- 数字签名
- 签名验证
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import base64
import os


class KeyManager:
    """密钥管理器"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def generate_keypair(self, student_id: str) -> tuple:
        """
        生成 RSA 密钥对
        
        Args:
            student_id: 学号（用于生成盐值）
            
        Returns:
            (private_key_pem, public_key_pem)
        """
        # 生成 RSA 密钥对（2048 位）
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        
        public_key = private_key.public_key()
        
        # 转换为 PEM 格式
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        从密码派生加密密钥（PBKDF2）
        
        Args:
            password: 学生密码
            salt: 盐值
            
        Returns:
            派生的密钥（32 字节）
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # 高迭代次数增加安全性
            backend=self.backend
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_private_key(self, private_key_pem: str, password: str) -> str:
        """
        用密码加密私钥
        
        Args:
            private_key_pem: 私钥（PEM 格式）
            password: 学生密码
            
        Returns:
            加密后的私钥（Base64 编码）
        """
        # 生成随机盐值
        salt = os.urandom(16)
        
        # 从密码派生密钥
        derived_key = self.derive_key(password, salt)
        
        # 使用 Fernet 加密
        fernet = Fernet(derived_key)
        encrypted = fernet.encrypt(private_key_pem.encode())
        
        # 返回：盐值 + 加密数据（Base64）
        result = base64.b64encode(salt + encrypted).decode('utf-8')
        
        return result
    
    def decrypt_private_key(self, encrypted_key_b64: str, password: str) -> str:
        """
        解密私钥
        
        Args:
            encrypted_key_b64: 加密的私钥（Base64）
            password: 学生密码
            
        Returns:
            私钥（PEM 格式）
        """
        # 解码
        data = base64.b64decode(encrypted_key_b64.encode())
        
        # 提取盐值和加密数据
        salt = data[:16]
        encrypted = data[16:]
        
        # 从密码派生密钥
        derived_key = self.derive_key(password, salt)
        
        # 解密
        fernet = Fernet(derived_key)
        private_pem = fernet.decrypt(encrypted).decode('utf-8')
        
        return private_pem
    
    def sign(self, private_key_pem: str, data: str) -> str:
        """
        数字签名
        
        Args:
            private_key_pem: 私钥（PEM 格式）
            data: 要签名的数据
            
        Returns:
            签名（Base64 编码）
        """
        # 加载私钥
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=self.backend
        )
        
        # 签名
        signature = private_key.sign(
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, public_key_pem: str, data: str, signature_b64: str) -> bool:
        """
        验证签名
        
        Args:
            public_key_pem: 公钥（PEM 格式）
            data: 原始数据
            signature_b64: 签名（Base64）
            
        Returns:
            是否验证通过
        """
        # 加载公钥
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=self.backend
        )
        
        # 解码签名
        signature = base64.b64decode(signature_b64.encode())
        
        try:
            public_key.verify(
                signature,
                data.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def get_public_key_from_private(self, private_key_pem: str) -> str:
        """
        从私钥提取公钥
        
        Args:
            private_key_pem: 私钥（PEM 格式）
            
        Returns:
            公钥（PEM 格式）
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=self.backend
        )
        
        public_key = private_key.public_key()
        
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')


# 测试
if __name__ == "__main__":
    km = KeyManager()
    
    # 生成密钥对
    private_pem, public_pem = km.generate_keypair("S_20260321_001")
    print("私钥（前 50 字符）:", private_pem[:50])
    print("公钥（前 50 字符）:", public_pem[:50])
    print("-" * 40)
    
    # 加密私钥
    password = "test_password_123"
    encrypted = km.encrypt_private_key(private_pem, password)
    print("加密后的私钥（前 50 字符）:", encrypted[:50])
    print("-" * 40)
    
    # 解密私钥
    decrypted = km.decrypt_private_key(encrypted, password)
    print("解密成功:", decrypted == private_pem)
    print("-" * 40)
    
    # 签名
    data = "Hello, 智慧大脑学院！"
    signature = km.sign(private_pem, data)
    print("签名（前 50 字符）:", signature[:50])
    print("-" * 40)
    
    # 验证签名
    valid = km.verify(public_pem, data, signature)
    print("签名验证:", "✓ 通过" if valid else "✗ 失败")
    
    # 验证错误数据
    invalid = km.verify(public_pem, "错误数据", signature)
    print("错误数据验证:", "✓ 通过" if invalid else "✗ 失败")
