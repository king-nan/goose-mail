"""
加密管理器

功能：
- AES-256-GCM 消息加密
- HMAC-SHA256 完整性校验
- 混合加密（RSA + AES）
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, hmac
import os
import base64
import json


class CryptoManager:
    """加密管理器"""
    
    def __init__(self):
        pass
    
    def generate_aes_key(self) -> bytes:
        """生成随机 AES-256 密钥（32 字节）"""
        return os.urandom(32)
    
    def encrypt_message(self, message: str, aes_key: bytes = None) -> dict:
        """
        AES-256-GCM 加密消息
        
        Args:
            message: 明文消息
            aes_key: AES 密钥（可选，不传则自动生成）
            
        Returns:
            {
                "ciphertext": base64 加密数据，
                "nonce": base64 随机数，
                "tag": base64 认证标签，
                "aes_key": base64 AES 密钥（用于 RSA 加密）
            }
        """
        if aes_key is None:
            aes_key = self.generate_aes_key()
        
        # 生成随机 nonce（12 字节）
        nonce = os.urandom(12)
        
        # AES-GCM 加密
        aesgcm = AESGCM(aes_key)
        ciphertext_with_tag = aesgcm.encrypt(nonce, message.encode(), None)
        
        # 分离密文和标签（标签在最后 16 字节）
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8'),
            "aes_key": base64.b64encode(aes_key).decode('utf-8')
        }
    
    def decrypt_message(self, encrypted_data: dict, aes_key: bytes = None) -> str:
        """
        AES-256-GCM 解密消息
        
        Args:
            encrypted_data: 加密数据（来自 encrypt_message）
            aes_key: AES 密钥（可选，不传则从 encrypted_data 获取）
            
        Returns:
            解密后的明文
        """
        # 解码
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        nonce = base64.b64decode(encrypted_data["nonce"])
        tag = base64.b64decode(encrypted_data["tag"])
        
        if aes_key is None:
            aes_key = base64.b64decode(encrypted_data["aes_key"])
        
        # AES-GCM 解密
        aesgcm = AESGCM(aes_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext + tag, None)
        
        return plaintext.decode('utf-8')
    
    def compute_hmac(self, data: str, key: bytes) -> str:
        """
        计算 HMAC-SHA256
        
        Args:
            data: 要签名的数据
            key: HMAC 密钥
            
        Returns:
            HMAC 值（Base64）
        """
        h = hmac.HMAC(key, hashes.SHA256())
        h.update(data.encode())
        return base64.b64encode(h.finalize()).decode('utf-8')
    
    def verify_hmac(self, data: str, hmac_b64: str, key: bytes) -> bool:
        """
        验证 HMAC
        
        Args:
            data: 原始数据
            hmac_b64: HMAC 值（Base64）
            key: HMAC 密钥
            
        Returns:
            是否验证通过
        """
        try:
            expected_hmac = base64.b64decode(hmac_b64.encode())
            h = hmac.HMAC(key, hashes.SHA256())
            h.update(data.encode())
            h.verify(expected_hmac)
            return True
        except Exception:
            return False
    
    def encrypt_for_recipient(self, message: str, recipient_public_key_pem: str, 
                               sender_private_key_pem: str) -> dict:
        """
        混合加密：为接收者加密消息
        
        流程：
        1. 生成随机 AES 密钥
        2. 用 AES 加密消息
        3. 用接收者公钥加密 AES 密钥
        4. 用发送者私钥签名
        
        Args:
            message: 明文消息
            recipient_public_key_pem: 接收者公钥
            sender_private_key_pem: 发送者私钥
            
        Returns:
            {
                "encrypted_message": AES 加密的消息，
                "encrypted_aes_key": RSA 加密的 AES 密钥，
                "sender_signature": 发送者签名，
                "timestamp": 时间戳
            }
        """
        from .keys import KeyManager
        
        km = KeyManager()
        
        # 1. 生成 AES 密钥并加密消息
        aes_key = self.generate_aes_key()
        encrypted_msg = self.encrypt_message(message, aes_key)
        
        # 2. 用接收者公钥加密 AES 密钥
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import serialization
        
        public_key = serialization.load_pem_public_key(
            recipient_public_key_pem.encode()
        )
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 3. 签名（对加密数据签名）
        data_to_sign = json.dumps({
            "ciphertext": encrypted_msg["ciphertext"],
            "nonce": encrypted_msg["nonce"]
        }, sort_keys=True)
        signature = km.sign(sender_private_key_pem, data_to_sign)
        
        import time
        return {
            "encrypted_message": encrypted_msg,
            "encrypted_aes_key": base64.b64encode(encrypted_aes_key).decode('utf-8'),
            "sender_signature": signature,
            "timestamp": time.time()
        }
    
    def decrypt_from_sender(self, encrypted_package: dict, 
                            recipient_private_key_pem: str,
                            sender_public_key_pem: str) -> str:
        """
        混合解密：解密发送者的消息
        
        Args:
            encrypted_package: 加密包（来自 encrypt_for_recipient）
            recipient_private_key_pem: 接收者私钥
            sender_public_key_pem: 发送者公钥
            
        Returns:
            解密后的明文
        """
        from .keys import KeyManager
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import serialization
        
        km = KeyManager()
        
        # 1. 验证签名
        data_to_verify = json.dumps({
            "ciphertext": encrypted_package["encrypted_message"]["ciphertext"],
            "nonce": encrypted_package["encrypted_message"]["nonce"]
        }, sort_keys=True)
        
        signature_valid = km.verify(
            sender_public_key_pem,
            data_to_verify,
            encrypted_package["sender_signature"]
        )
        if not signature_valid:
            raise ValueError("签名验证失败")
        
        # 2. 用接收者私钥解密 AES 密钥
        private_key = serialization.load_pem_private_key(
            recipient_private_key_pem.encode(),
            password=None
        )
        encrypted_aes_key = base64.b64decode(encrypted_package["encrypted_aes_key"])
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 3. 用 AES 密钥解密消息
        return self.decrypt_message(encrypted_package["encrypted_message"], aes_key)


# 测试
if __name__ == "__main__":
    cm = CryptoManager()
    
    # 测试 AES 加密
    print("=== AES-256-GCM 加密测试 ===")
    message = "你好，智慧大脑学院！"
    encrypted = cm.encrypt_message(message)
    print(f"原文：{message}")
    print(f"密文：{encrypted['ciphertext'][:50]}...")
    decrypted = cm.decrypt_message(encrypted)
    print(f"解密：{decrypted}")
    print(f"匹配：{message == decrypted}")
    print("-" * 40)
    
    # 测试 HMAC
    print("=== HMAC-SHA256 测试 ===")
    hmac_key = os.urandom(32)
    data = "测试数据"
    hmac_val = cm.compute_hmac(data, hmac_key)
    print(f"HMAC: {hmac_val[:50]}...")
    print(f"验证：{cm.verify_hmac(data, hmac_val, hmac_key)}")
    print(f"错误验证：{cm.verify_hmac('错误数据', hmac_val, hmac_key)}")
