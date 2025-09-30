import json
import os


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config()
        return self.default_config()
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def default_config(self):
        """默认配置"""
        return {
            "target_path": "",
            "last_selected_image": "",
            "custom_images": []
        }
    
    def get_target_path(self):
        """获取目标路径"""
        return self.config.get("target_path", "")
    
    def set_target_path(self, path):
        """设置目标路径"""
        self.config["target_path"] = path
        self.save()
    
    def get_last_selected_image(self):
        """获取最后选中的图片"""
        return self.config.get("last_selected_image", "")
    
    def set_last_selected_image(self, image_name):
        """设置最后选中的图片"""
        self.config["last_selected_image"] = image_name
        self.save()
    
    def get_custom_images(self):
        """获取自定义图片列表"""
        return self.config.get("custom_images", [])
    
    def add_custom_image(self, image_info):
        """添加自定义图片"""
        if "custom_images" not in self.config:
            self.config["custom_images"] = []
        self.config["custom_images"].append(image_info)
        self.save()
    
    def remove_custom_image(self, filename):
        """移除自定义图片"""
        if "custom_images" in self.config:
            self.config["custom_images"] = [
                img for img in self.config["custom_images"] 
                if img.get("filename") != filename
            ]
            self.save()
    
    def update_custom_image_name(self, old_filename, new_display_name):
        """更新自定义图片显示名称"""
        if "custom_images" in self.config:
            for img in self.config["custom_images"]:
                if img.get("filename") == old_filename:
                    img["display_name"] = new_display_name
                    break
            self.save()
