"""
区块链式审计日志

特点：
- 每块包含前一块的哈希（链条）
- 不可篡改（修改任意块会破坏后续所有块）
- 每块都有操作者签名
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class AuditLogger:
    """区块链式审计日志"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.audit_file = self.data_dir / "audit.jsonl"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _compute_hash(self, block_data: dict) -> str:
        """计算区块哈希"""
        # 移除 hash 字段本身（计算时不包含）
        data_copy = {k: v for k, v in block_data.items() if k != "hash"}
        data_str = json.dumps(data_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _get_last_block(self) -> Optional[dict]:
        """获取最后一个区块"""
        if not self.audit_file.exists():
            return None
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return None
            last_line = lines[-1].strip()
            if last_line:
                return json.loads(last_line)
        return None
    
    def _get_last_hash(self) -> str:
        """获取最后一个区块的哈希"""
        last_block = self._get_last_block()
        if last_block is None:
            return "0"  # 创世区块的前哈希为 "0"
        return last_block["hash"]
    
    def log(self, action: str, actor: str, target: str = None, 
            data: dict = None, signature: str = "system") -> dict:
        """
        记录审计日志（新区块）
        
        Args:
            action: 操作类型（如 student_enroll, message_send）
            actor: 操作者
            target: 目标（如学号）
            data: 操作数据
            signature: 操作者签名（可选）
            
        Returns:
            新区块
        """
        # 获取前一个区块的哈希
        prev_hash = self._get_last_hash()
        
        # 获取序列号
        last_block = self._get_last_block()
        seq = (last_block["seq"] + 1) if last_block else 1
        
        # 计算数据哈希
        data_str = json.dumps(data or {}, sort_keys=True, ensure_ascii=False)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # 构建区块
        block = {
            "seq": seq,
            "prev_hash": prev_hash,
            "action": action,
            "actor": actor,
            "target": target,
            "data_hash": data_hash,
            "signature": signature,
            "timestamp": datetime.now().isoformat(),
            "hash": ""  # 待计算
        }
        
        # 计算当前区块哈希
        block["hash"] = self._compute_hash(block)
        
        # 写入文件
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(block, ensure_ascii=False) + "\n")
        
        return block
    
    def get_chain(self, start_seq: int = 1, limit: int = 100) -> List[dict]:
        """
        获取区块链
        
        Args:
            start_seq: 起始序列号
            limit: 最多返回多少块
            
        Returns:
            区块列表
        """
        if not self.audit_file.exists():
            return []
        
        blocks = []
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    block = json.loads(line)
                    if block["seq"] >= start_seq:
                        blocks.append(block)
                        if len(blocks) >= limit:
                            break
        
        return blocks
    
    def verify_chain(self) -> dict:
        """
        验证整个区块链是否被篡改
        
        Returns:
            {
                "valid": bool,
                "total_blocks": int,
                "error_at": int or None  # 如果有错误，指出位置
            }
        """
        if not self.audit_file.exists():
            return {"valid": True, "total_blocks": 0, "error_at": None}
        
        blocks = []
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    blocks.append(json.loads(line))
        
        if not blocks:
            return {"valid": True, "total_blocks": 0, "error_at": None}
        
        # 验证每个区块
        prev_hash = "0"
        for i, block in enumerate(blocks):
            # 验证 prev_hash
            if block["prev_hash"] != prev_hash:
                return {
                    "valid": False,
                    "total_blocks": len(blocks),
                    "error_at": i + 1,
                    "error_type": "prev_hash_mismatch"
                }
            
            # 验证区块哈希
            computed_hash = self._compute_hash(block)
            if block["hash"] != computed_hash:
                return {
                    "valid": False,
                    "total_blocks": len(blocks),
                    "error_at": i + 1,
                    "error_type": "hash_mismatch"
                }
            
            prev_hash = block["hash"]
        
        return {"valid": True, "total_blocks": len(blocks), "error_at": None}
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        verification = self.verify_chain()
        return {
            "total_blocks": verification["total_blocks"],
            "chain_valid": verification["valid"],
            "last_block_time": self._get_last_block()["timestamp"] if verification["total_blocks"] > 0 else None
        }
    
    def search(self, action: str = None, actor: str = None, 
               target: str = None) -> List[dict]:
        """
        搜索审计日志
        
        Args:
            action: 操作类型过滤
            actor: 操作者过滤
            target: 目标过滤
            
        Returns:
            匹配的区块列表
        """
        blocks = self.get_chain(limit=10000)  # 获取所有
        results = []
        
        for block in blocks:
            if action and block["action"] != action:
                continue
            if actor and block["actor"] != actor:
                continue
            if target and block["target"] != target:
                continue
            results.append(block)
        
        return results


# 测试
if __name__ == "__main__":
    logger = AuditLogger(data_dir="./data")
    
    print("=== 区块链审计日志测试 ===\n")
    
    # 记录几个操作
    print("1. 记录操作...")
    logger.log("student_enroll", "智虾", "S_20260321_001", {"name": "小虾米"})
    logger.log("message_send", "智虾", "S_20260321_001", {"message": "欢迎入学"})
    logger.log("assignment_submit", "小虾米", "S_20260321_001", {"assignment": "L1-001"})
    
    # 获取统计
    stats = logger.get_stats()
    print(f"2. 统计信息：{stats}\n")
    
    # 获取链条
    blocks = logger.get_chain()
    print("3. 区块链:")
    for block in blocks:
        print(f"   #{block['seq']} {block['action']} -> {block['target']}")
        print(f"      哈希：{block['hash'][:20]}...")
    
    # 验证
    print("\n4. 验证链条:")
    verification = logger.verify_chain()
    print(f"   有效性：{'✓ 有效' if verification['valid'] else '✗ 无效'}")
    print(f"   总块数：{verification['total_blocks']}")
    
    # 搜索
    print("\n5. 搜索 'student_enroll':")
    results = logger.search(action="student_enroll")
    for r in results:
        print(f"   找到：{r['target']}")
