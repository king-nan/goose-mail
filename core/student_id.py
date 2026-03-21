"""
学号生成器

学号格式：S_YYYYMMDD_序号
示例：S_20260321_001

特点：
- 终身唯一
- 包含日期信息
- 序号每天重置（001-999）
"""

from datetime import datetime
import json
import os
from pathlib import Path


class StudentIDGenerator:
    """学号生成器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.counter_file = self.data_dir / "student_counter.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_counter(self) -> dict:
        """加载计数器"""
        if self.counter_file.exists():
            with open(self.counter_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"current_date": None, "counter": 0}
    
    def _save_counter(self, counter_data: dict):
        """保存计数器"""
        with open(self.counter_file, 'w', encoding='utf-8') as f:
            json.dump(counter_data, f, ensure_ascii=False, indent=2)
    
    def generate(self, date: datetime = None) -> str:
        """
        生成新学号
        
        Args:
            date: 日期，默认使用当前日期
            
        Returns:
            学号，格式：S_YYYYMMDD_序号
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y%m%d")
        
        # 加载计数器
        counter_data = self._load_counter()
        
        # 如果日期变化，重置计数器
        if counter_data["current_date"] != date_str:
            counter_data["current_date"] = date_str
            counter_data["counter"] = 0
        
        # 计数器 +1
        counter_data["counter"] += 1
        
        if counter_data["counter"] > 999:
            raise ValueError("当天学号已达上限（999 个）")
        
        # 保存计数器
        self._save_counter(counter_data)
        
        # 生成学号
        student_id = f"S_{date_str}_{counter_data['counter']:03d}"
        
        return student_id
    
    def get_union_id(self, student_id: str) -> str:
        """
        根据学号生成 Union ID（飞书格式）
        
        Args:
            student_id: 学号
            
        Returns:
            Union ID，格式：on_S_YYYYMMDD_序号
        """
        return f"on_{student_id}"
    
    def parse(self, student_id: str) -> dict:
        """
        解析学号信息
        
        Args:
            student_id: 学号
            
        Returns:
            解析结果：{date, sequence, union_id}
        """
        if not student_id.startswith("S_"):
            raise ValueError("无效的学号格式")
        
        parts = student_id.split("_")
        if len(parts) != 3:
            raise ValueError("无效的学号格式")
        
        date_str = parts[1]
        sequence = int(parts[2])
        
        return {
            "date": datetime.strptime(date_str, "%Y%m%d"),
            "sequence": sequence,
            "union_id": self.get_union_id(student_id)
        }
    
    def validate(self, student_id: str) -> bool:
        """
        验证学号格式
        
        Args:
            student_id: 学号
            
        Returns:
            是否有效
        """
        try:
            self.parse(student_id)
            return True
        except (ValueError, IndexError):
            return False


# 测试
if __name__ == "__main__":
    gen = StudentIDGenerator(data_dir="./data")
    
    # 生成 3 个学号
    for i in range(3):
        sid = gen.generate()
        print(f"学号：{sid}")
        print(f"Union ID: {gen.get_union_id(sid)}")
        print(f"解析：{gen.parse(sid)}")
        print("-" * 40)
