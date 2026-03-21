"""
二维码勋章生成器

功能：
- 生成二维码（包含学号）
- 制作勋章图片（PNG）
- 支持自定义模板
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os


class BadgeGenerator:
    """二维码勋章生成器"""
    
    def __init__(self, badges_dir: str = "./badges"):
        self.badges_dir = Path(badges_dir)
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        self.badges_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_qrcode(self, student_id: str) -> Image.Image:
        """
        生成二维码图片
        
        Args:
            student_id: 学号
            
        Returns:
            PIL Image 对象
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_id)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def generate_badge(self, student_id: str, name: str, level: str = "L1") -> dict:
        """
        生成完整勋章（包含二维码 + 文字信息）
        
        Args:
            student_id: 学号
            name: 学生姓名
            level: 等级（L1/L2/L3/L4）
            
        Returns:
            {
                "png_path": PNG 文件路径，
                "svg_path": SVG 文件路径（可选），
                "student_id": 学号
            }
        """
        # 创建 300x400 的白色背景
        width, height = 300, 400
        badge = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(badge)
        
        # 尝试加载字体（使用系统字体）
        try:
            # 尝试常见中文字体路径
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
                "C:\\Windows\\Fonts\\simhei.ttf",  # Windows
            ]
            font_large = None
            font_small = None
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_large = ImageFont.truetype(font_path, 24)
                    font_small = ImageFont.truetype(font_path, 14)
                    break
            
            if font_large is None:
                # 使用默认字体
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # 1. 顶部标题
        title = "🧠 智慧大脑学院"
        draw.text((width // 2, 20), title, fill='black', anchor='mm', font=font_large)
        
        subtitle = "学思通 · 学员勋章"
        draw.text((width // 2, 45), subtitle, fill='gray', anchor='mm', font=font_small)
        
        # 2. 生成二维码
        qr_img = self.generate_qrcode(student_id)
        qr_img = qr_img.resize((150, 150), Image.Resampling.LANCZOS)
        
        # 居中放置二维码
        qr_x = (width - 150) // 2
        qr_y = 80
        badge.paste(qr_img, (qr_x, qr_y))
        
        # 3. 学号（二维码下方）
        draw.text((width // 2, 250), student_id, fill='black', 
                 anchor='mm', font=font_large)
        
        # 4. 姓名和等级
        name_level = f"{name} · {level}"
        draw.text((width // 2, 280), name_level, fill='gray', 
                 anchor='mm', font=font_small)
        
        # 5. 入学日期
        from datetime import datetime
        date_str = datetime.now().strftime("%Y.%m.%d")
        draw.text((width // 2, 305), date_str, fill='lightgray', 
                 anchor='mm', font=font_small)
        
        # 6. 底部标语
        slogan = "🦐 让每只虾米找到方向"
        draw.text((width // 2, 350), slogan, fill='gray', 
                 anchor='mm', font=font_small)
        
        # 保存 PNG
        png_path = self.badges_dir / f"{student_id}.png"
        badge.save(png_path, 'PNG')
        
        # 生成 SVG（简化版）
        svg_path = self._generate_svg(student_id, name, level)
        
        return {
            "png_path": str(png_path),
            "svg_path": str(svg_path),
            "student_id": student_id
        }
    
    def _generate_svg(self, student_id: str, name: str, level: str) -> str:
        """
        生成 SVG 矢量版勋章
        
        Args:
            student_id: 学号
            name: 姓名
            level: 等级
            
        Returns:
            SVG 文件路径
        """
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="400" xmlns="http://www.w3.org/2000/svg">
  <!-- 背景 -->
  <rect width="300" height="400" fill="white"/>
  
  <!-- 标题 -->
  <text x="150" y="30" text-anchor="middle" font-size="20" fill="black">🧠 智慧大脑学院</text>
  <text x="150" y="50" text-anchor="middle" font-size="12" fill="gray">学思通 · 学员勋章</text>
  
  <!-- 二维码占位（实际使用时替换为真实二维码） -->
  <rect x="75" y="80" width="150" height="150" fill="none" stroke="black" stroke-width="2"/>
  <text x="150" y="160" text-anchor="middle" font-size="10" fill="gray">二维码</text>
  
  <!-- 学号 -->
  <text x="150" y="260" text-anchor="middle" font-size="18" fill="black">{student_id}</text>
  
  <!-- 姓名和等级 -->
  <text x="150" y="285" text-anchor="middle" font-size="14" fill="gray">{name} · {level}</text>
  
  <!-- 日期 -->
  <text x="150" y="310" text-anchor="middle" font-size="12" fill="lightgray">{__import__('datetime').datetime.now().strftime("%Y.%m.%d")}</text>
  
  <!-- 标语 -->
  <text x="150" y="360" text-anchor="middle" font-size="12" fill="gray">🦐 让每只虾米找到方向</text>
</svg>'''
        
        svg_path = self.badges_dir / f"{student_id}.svg"
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(svg_path)
    
    def get_badge_path(self, student_id: str) -> str:
        """
        获取勋章文件路径
        
        Args:
            student_id: 学号
            
        Returns:
            PNG 文件路径（如果存在）
        """
        png_path = self.badges_dir / f"{student_id}.png"
        if png_path.exists():
            return str(png_path)
        return None


# 测试
if __name__ == "__main__":
    bg = BadgeGenerator(badges_dir="./badges")
    
    print("=== 二维码勋章生成测试 ===\n")
    
    # 生成勋章
    result = bg.generate_badge("S_20260321_001", "小虾米", "L1")
    
    print(f"学号：{result['student_id']}")
    print(f"PNG: {result['png_path']}")
    print(f"SVG: {result['svg_path']}")
    print("\n勋章已生成！")
