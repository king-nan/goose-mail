"""
访客学号生成器

功能：
- 生成访客学号（G_YYYYMMDD_序号）
- 管理访客计数器
- 访客转正式学员
"""

import json
from pathlib import Path
from datetime import datetime


class GuestIDGenerator:
    """访客学号生成器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.counter_file = self.data_dir / "guest_counter.json"
        self._ensure_data_dir()
        self._init_counter()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_counter(self):
        """初始化计数器"""
        if not self.counter_file.exists():
            self._save_counter({"date": datetime.now().strftime("%Y%m%d"), "count": 0})
    
    def _load_counter(self) -> dict:
        """加载计数器"""
        with open(self.counter_file, 'r') as f:
            return json.load(f)
    
    def _save_counter(self, counter: dict):
        """保存计数器"""
        with open(self.counter_file, 'w') as f:
            json.dump(counter, f, indent=2)
    
    def generate(self) -> str:
        """
        生成访客学号
        
        Returns:
            访客学号（格式：G_YYYYMMDD_序号）
        """
        counter = self._load_counter()
        today = datetime.now().strftime("%Y%m%d")
        
        # 如果是新的一天，重置计数器
        if counter["date"] != today:
            counter = {"date": today, "count": 0}
        
        # 生成学号
        counter["count"] += 1
        guest_id = f"G_{today}_{counter['count']:03d}"
        
        # 保存计数器
        self._save_counter(counter)
        
        return guest_id
    
    def get_union_id(self, guest_id: str) -> str:
        """
        生成 Union ID
        
        Args:
            guest_id: 访客学号
            
        Returns:
            Union ID（格式：on_G_xxx）
        """
        return f"on_{guest_id}"
    
    def upgrade_to_student(self, guest_id: str, student_id: str) -> bool:
        """
        访客转为正式学员（记录映射关系）
        
        Args:
            guest_id: 访客学号
            student_id: 正式学号
            
        Returns:
            是否成功
        """
        mapping_file = self.data_dir / "guest_student_mapping.json"
        
        # 加载映射
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)
        else:
            mapping = {}
        
        # 添加映射
        mapping[guest_id] = {
            "student_id": student_id,
            "upgraded_at": datetime.now().isoformat()
        }
        
        # 保存映射
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        return True
    
    def get_student_id(self, guest_id: str) -> str:
        """
        根据访客学号获取正式学号
        
        Args:
            guest_id: 访客学号
            
        Returns:
            正式学号（如果没有则返回 None）
        """
        mapping_file = self.data_dir / "guest_student_mapping.json"
        
        if not mapping_file.exists():
            return None
        
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        
        if guest_id in mapping:
            return mapping[guest_id]["student_id"]
        
        return None


# 测试
if __name__ == "__main__":
    gen = GuestIDGenerator(data_dir="./data")
    
    print("=== 访客学号生成器测试 ===\n")
    
    # 生成访客学号
    print("1. 生成访客学号:")
    for i in range(3):
        guest_id = gen.generate()
        union_id = gen.get_union_id(guest_id)
        print(f"   {guest_id} -> {union_id}")
    
    # 访客转正式
    print("\n2. 访客转正式学员:")
    gen.upgrade_to_student("G_20260322_001", "S_20260322_001")
    print("   G_20260322_001 -> S_20260322_001")
    
    # 查询映射
    print("\n3. 查询映射:")
    student_id = gen.get_student_id("G_20260322_001")
    print(f"   G_20260322_001 的正式学号：{student_id}")
