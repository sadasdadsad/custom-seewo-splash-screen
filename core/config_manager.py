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
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def default_config(self):
        """默认配置"""
        return {
            "target_path": "",
            "target_path_history": [],  # 新增:历史路径记录
            "last_selected_image": "",
            "custom_images": [],
            "auto_detect_on_startup": True  # 新增:启动时是否自动检测
        }
    
    def get_target_path(self):
        """获取目标路径"""
        return self.config.get("target_path", "")
    
    def set_target_path(self, path):
        """设置目标路径"""
        if path:
            self.config["target_path"] = path
            # 添加到历史记录
            self.add_to_path_history(path)
        else:
            self.config["target_path"] = ""
        self.save()
    
    def add_to_path_history(self, path):
        """添加路径到历史记录"""
        if "target_path_history" not in self.config:
            self.config["target_path_history"] = []
        
        # 如果路径已存在,先移除
        if path in self.config["target_path_history"]:
            self.config["target_path_history"].remove(path)
        
        # 添加到列表开头
        self.config["target_path_history"].insert(0, path)
        
        # 只保留最近5个路径
        self.config["target_path_history"] = self.config["target_path_history"][:5]
    
    def get_path_history(self):
        """获取路径历史记录"""
        return self.config.get("target_path_history", [])
    
    def clear_invalid_history(self):
        """清理无效的历史路径"""
        if "target_path_history" not in self.config:
            return
        
        valid_paths = [
            path for path in self.config["target_path_history"]
            if os.path.exists(path)
        ]
        self.config["target_path_history"] = valid_paths
        self.save()
    
    def get_auto_detect_on_startup(self):
        """获取启动时是否自动检测"""
        return self.config.get("auto_detect_on_startup", True)
    
    def set_auto_detect_on_startup(self, enabled):
        """设置启动时是否自动检测"""
        self.config["auto_detect_on_startup"] = enabled
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
