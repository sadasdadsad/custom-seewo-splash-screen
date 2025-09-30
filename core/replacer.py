import os
import shutil
import stat
from datetime import datetime


class ImageReplacer:
    """图片替换器"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def has_backup(self, target_path):
        """检查是否已存在备份"""
        if not target_path or not os.path.exists(target_path):
            return False
        
        base_name = os.path.basename(target_path)
        # 检查backups目录下是否有以该文件名开头的备份
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(os.path.splitext(base_name)[0] + "_"):
                return True
        return False
    
    def backup_original(self, target_path):
        """备份原始文件"""
        if not os.path.exists(target_path):
            return False, "目标文件不存在"
        
        # 检查是否已有备份
        if self.has_backup(target_path):
            return True, "检测到已有备份，跳过备份步骤"
        
        try:
            # 生成备份文件名
            base_name = os.path.basename(target_path)
            name_without_ext = os.path.splitext(base_name)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name_without_ext}_{timestamp}.png"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 执行备份
            shutil.copy2(target_path, backup_path)
            return True, f"已备份原始文件: {backup_filename}"
        except Exception as e:
            return False, f"备份失败: {str(e)}"
    
    def remove_readonly(self, filepath):
        """移除文件只读属性"""
        try:
            if os.path.exists(filepath):
                os.chmod(filepath, stat.S_IWRITE)
            return True
        except:
            return False
    
    def set_readonly(self, filepath):
        """设置文件只读属性"""
        try:
            if os.path.exists(filepath):
                os.chmod(filepath, stat.S_IREAD)
            return True
        except:
            return False
    
    def replace_image(self, source_path, target_path):
        """替换图片"""
        if not os.path.exists(source_path):
            return False, "源图片不存在"
        
        if not os.path.exists(target_path):
            return False, "目标路径不存在"
        
        try:
            # 备份原始文件
            backup_success, backup_msg = self.backup_original(target_path)
            if not backup_success and not self.has_backup(target_path):
                return False, backup_msg
            
            # 移除只读属性
            was_readonly = False
            try:
                # 检查是否为只读
                if not os.access(target_path, os.W_OK):
                    was_readonly = True
                    self.remove_readonly(target_path)
            except:
                pass
            
            # 执行替换
            shutil.copy2(source_path, target_path)
            
            # 恢复只读属性
            if was_readonly:
                self.set_readonly(target_path)
            
            return True, f"替换成功 | {backup_msg}"
        except PermissionError:
            return False, "文件被占用，无法替换"
        except Exception as e:
            return False, f"替换失败: {str(e)}"
    
    def restore_backup(self, target_path):
        """从备份还原"""
        if not os.path.exists(target_path):
            return False, "目标路径不存在"
        
        # 查找备份文件
        base_name = os.path.basename(target_path)
        name_without_ext = os.path.splitext(base_name)[0]
        
        backup_file = None
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(name_without_ext + "_"):
                backup_file = filename
                break
        
        if not backup_file:
            return False, "未找到备份文件"
        
        backup_path = os.path.join(self.backup_dir, backup_file)
        
        try:
            # 移除只读属性
            was_readonly = False
            try:
                if not os.access(target_path, os.W_OK):
                    was_readonly = True
                    self.remove_readonly(target_path)
            except:
                pass
            
            # 执行还原
            shutil.copy2(backup_path, target_path)
            
            # 恢复只读属性
            if was_readonly:
                self.set_readonly(target_path)
            
            return True, "已还原备份"
        except PermissionError:
            return False, "文件被占用，无法还原"
        except Exception as e:
            return False, f"还原失败: {str(e)}"
