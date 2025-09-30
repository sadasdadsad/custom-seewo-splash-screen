import os
import shutil
from PIL import Image


class ImageManager:
    """图片管理器"""
    
    def __init__(self):
        self.preset_dir = "assets/presets"
        self.custom_dir = "assets/custom"
    
    def get_preset_images(self):
        """获取预设图片列表"""
        images = []
        if os.path.exists(self.preset_dir):
            for filename in os.listdir(self.preset_dir):
                if filename.lower().endswith('.png'):
                    images.append({
                        "type": "preset",
                        "filename": filename,
                        "display_name": os.path.splitext(filename)[0],
                        "path": os.path.join(self.preset_dir, filename)
                    })
        return images
    
    def get_custom_images(self):
        """获取自定义图片列表"""
        images = []
        if os.path.exists(self.custom_dir):
            for filename in os.listdir(self.custom_dir):
                if filename.lower().endswith('.png'):
                    images.append({
                        "type": "custom",
                        "filename": filename,
                        "display_name": os.path.splitext(filename)[0],
                        "path": os.path.join(self.custom_dir, filename)
                    })
        return images
    
    def import_image(self, source_path, display_name=None):
        """导入图片到自定义目录"""
        if not source_path.lower().endswith('.png'):
            return False, "仅支持PNG格式"
        
        if not os.path.exists(source_path):
            return False, "文件不存在"
        
        # 验证是否为有效的PNG图片
        try:
            img = Image.open(source_path)
            img.verify()
        except:
            return False, "无效的PNG图片"
        
        # 生成文件名
        if display_name:
            filename = display_name if display_name.endswith('.png') else f"{display_name}.png"
        else:
            filename = os.path.basename(source_path)
        
        dest_path = os.path.join(self.custom_dir, filename)
        
        # 如果文件已存在，添加序号
        counter = 1
        base_name = os.path.splitext(filename)[0]
        while os.path.exists(dest_path):
            filename = f"{base_name}_{counter}.png"
            dest_path = os.path.join(self.custom_dir, filename)
            counter += 1
        
        try:
            shutil.copy2(source_path, dest_path)
            return True, filename
        except Exception as e:
            return False, f"导入失败: {str(e)}"
    
    def delete_custom_image(self, filename):
        """删除自定义图片"""
        file_path = os.path.join(self.custom_dir, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except:
            return False
    
    def rename_custom_image(self, old_filename, new_display_name):
        """重命名自定义图片"""
        old_path = os.path.join(self.custom_dir, old_filename)
        new_filename = new_display_name if new_display_name.endswith('.png') else f"{new_display_name}.png"
        new_path = os.path.join(self.custom_dir, new_filename)
        
        try:
            if os.path.exists(old_path) and not os.path.exists(new_path):
                os.rename(old_path, new_path)
                return True, new_filename
            return False, "重命名失败"
        except Exception as e:
            return False, f"重命名失败: {str(e)}"
