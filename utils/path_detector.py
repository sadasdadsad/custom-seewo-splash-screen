import os
import glob


class PathDetector:
    """检测希沃白板启动图片路径"""
    
    @staticmethod
    def detect_banner_paths():
        """检测Banner.png路径"""
        paths = []
        users_dir = "C:\\Users"
        
        if os.path.exists(users_dir):
            for user_folder in os.listdir(users_dir):
                banner_path = os.path.join(
                    users_dir, 
                    user_folder, 
                    "AppData\\Roaming\\Seewo\\EasiNote5\\Resources\\Banner\\Banner.png"
                )
                if os.path.exists(banner_path):
                    paths.append(banner_path)
        
        return paths
    
    @staticmethod
    def detect_splashscreen_paths():
        """检测SplashScreen.png路径"""
        paths = []
        
        # 检测 Program Files (x86)
        base_path_x86 = "C:\\Program Files (x86)\\Seewo\\EasiNote5"
        if os.path.exists(base_path_x86):
            pattern = os.path.join(base_path_x86, "EasiNote5*", "Main", "Assets", "SplashScreen.png")
            paths.extend(glob.glob(pattern))
        
        # 检测 Program Files
        base_path = "C:\\Program Files\\Seewo\\EasiNote5"
        if os.path.exists(base_path):
            pattern = os.path.join(base_path, "EasiNote5*", "Main", "Assets", "SplashScreen.png")
            paths.extend(glob.glob(pattern))
        
        return paths
    
    @staticmethod
    def detect_all_paths():
        """检测所有可能的路径"""
        all_paths = []
        all_paths.extend(PathDetector.detect_banner_paths())
        all_paths.extend(PathDetector.detect_splashscreen_paths())
        return all_paths
