import os
import sys
import shutil
import subprocess
from pathlib import Path


class Builder:
    """应用打包构建器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"
        self.app_name = "SeewoSplash"
        self.main_script = "main.py"
        
    def clean(self):
        """清理之前的构建文件"""
        print("=" * 60)
        print("步骤 1: 清理旧的构建文件...")
        print("=" * 60)
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"正在删除: {dir_path}")
                shutil.rmtree(dir_path, ignore_errors=True)
        
        # 删除 .spec 文件
        spec_files = list(self.root_dir.glob("*.spec"))
        for spec_file in spec_files:
            print(f"正在删除: {spec_file}")
            spec_file.unlink()
        
        print("✓ 清理完成\n")
    
    def check_dependencies(self):
        """检查依赖"""
        print("=" * 60)
        print("步骤 2: 检查依赖...")
        print("=" * 60)
        
        try:
            import PyInstaller
            print(f"✓ PyInstaller 版本: {PyInstaller.__version__}")
        except ImportError:
            print("✗ PyInstaller 未安装")
            print("正在安装 PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller 安装完成")
        
        try:
            import PyQt6
            print(f"✓ PyQt6 已安装")
        except ImportError:
            print("✗ PyQt6 未安装，请先安装: pip install PyQt6")
            sys.exit(1)
        
        print("✓ 依赖检查完成\n")
    
    def create_icon(self):
        """创建/检查图标文件"""
        print("=" * 60)
        print("步骤 3: 检查图标文件...")
        print("=" * 60)
        
        icon_path = self.root_dir / "assets" / "icon.ico"
        
        if not icon_path.exists():
            print(f"⚠ 未找到图标文件: {icon_path}")
            print("  将使用默认图标")
            return None
        else:
            print(f"✓ 找到图标文件: {icon_path}")
            return str(icon_path)
    
    def collect_data_files(self):
        """收集需要打包的数据文件"""
        print("=" * 60)
        print("步骤 4: 收集数据文件...")
        print("=" * 60)
        
        data_files = []
        separator = ";" if sys.platform == "win32" else ":"
        
        # 只打包 assets/presets 目录（预设图片）
        presets_dir = self.root_dir / "assets" / "presets"
        if presets_dir.exists():
            data_files.append((str(presets_dir), "assets/presets"))
            print(f"✓ 添加预设图片目录: {presets_dir}")
            
            # 统计预设图片数量
            image_files = list(presets_dir.glob("*.png"))
            print(f"  共找到 {len(image_files)} 个预设图片")
            for img in image_files:
                print(f"    - {img.name}")
        else:
            print(f"⚠ 未找到预设图片目录: {presets_dir}")
        
        # 不打包 images/custom 目录（用户自定义图片目录，运行时创建）
        custom_dir = self.root_dir / "images" / "custom"
        if custom_dir.exists():
            print(f"⚠ 跳过自定义图片目录: {custom_dir} (运行时创建)")
        
        if not data_files:
            print("⚠ 未找到需要打包的数据文件")
        
        print(f"✓ 数据文件收集完成\n")
        return data_files
    
    def build(self):
        """执行打包"""
        print("=" * 60)
        print("步骤 5: 开始打包（非单文件模式）...")
        print("=" * 60)
        
        # 准备 PyInstaller 参数
        icon_path = self.create_icon()
        data_files = self.collect_data_files()
        
        pyinstaller_args = [
            "pyinstaller",
            "--name", self.app_name,
            "--onedir",  # 使用目录模式（非单文件）
            "--windowed",  # 不显示控制台窗口
            "--clean",  # 清理临时文件
            "--noconfirm",  # 不确认覆盖
        ]
        
        # 添加图标
        if icon_path:
            pyinstaller_args.extend(["--icon", icon_path])
        
        # 添加数据文件
        separator = ";" if sys.platform == "win32" else ":"
        for src, dst in data_files:
            pyinstaller_args.extend(["--add-data", f"{src}{separator}{dst}"])
        
        # 隐藏不必要的导入
        hidden_imports = [
            "PyQt6.QtCore",
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
        ]
        
        for module in hidden_imports:
            pyinstaller_args.extend(["--hidden-import", module])
        
        # 添加主脚本
        pyinstaller_args.append(str(self.main_script))
        
        # 显示完整命令
        print("执行命令:")
        print(" ".join(pyinstaller_args))
        print()
        
        # 执行打包
        try:
            subprocess.check_call(pyinstaller_args)
            print("\n✓ 打包完成")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ 打包失败: {e}")
            sys.exit(1)
    
    def post_build(self):
        """打包后处理"""
        print("\n" + "=" * 60)
        print("步骤 6: 打包后处理...")
        print("=" * 60)
        
        # 在目录模式下，可执行文件在 dist/应用名/ 目录下
        exe_dir = self.dist_dir / self.app_name
        
        if not exe_dir.exists():
            print(f"✗ 未找到输出目录: {exe_dir}")
            return
        
        # 创建必要的目录结构（在可执行文件目录外部）
        dirs_to_create = [
            exe_dir / "images" / "custom",  # 自定义图片目录
            exe_dir / "backup",             # 备份目录
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ 创建目录: {dir_path.relative_to(self.dist_dir)}")
        
        # 复制 README
        # readme_src = self.root_dir / "README.md"
        # if readme_src.exists():
        #     readme_dst = exe_dir / "使用说明.txt"
        #     shutil.copy2(readme_src, readme_dst)
        #     print(f"✓ 复制使用说明: {readme_dst.relative_to(self.dist_dir)}")
        
        # 创建一个启动说明文件
        # startup_guide = exe_dir / "运行说明.txt"
        # with open(startup_guide, "w", encoding="utf-8") as f:
        #     f.write(f"希沃白板启动图修改器\n")
        #     f.write("=" * 50 + "\n\n")
        #     f.write(f"运行程序：双击 {self.app_name}.exe\n\n")
        #     f.write("目录说明：\n")
        #     f.write("  - _internal/assets/presets/  预设图片目录（只读）\n")
        #     f.write("  - images/custom/             自定义图片目录（可��）\n")
        #     f.write("  - backup/                    备份目录（可写）\n")
        #     f.write("  - config.json                配置文件（自动生成）\n\n")
        #     f.write("注意事项：\n")
        #     f.write("  1. 不要删除或移动 _internal 目录\n")
        #     f.write("  2. 首次运行需要检测启动图片路径\n")
        #     f.write("  3. 需要管理员权限才能替换系统文件\n")
        #     f.write("  4. 可以将自己的图片放到 images/custom/ 目录\n")
        
        # print(f"✓ 创建运行说明: {startup_guide.relative_to(self.dist_dir)}")
        
        # 验证预设图片是否正确复制
        preset_dir = exe_dir / "_internal" / "assets" / "presets"
        if preset_dir.exists():
            image_files = list(preset_dir.glob("*.png"))
            print(f"✓ 预设图片验证: 共 {len(image_files)} 个文件")
            for img in image_files:
                print(f"    - {img.name}")
        else:
            print(f"⚠ 警告: 预设图片目录不存在: {preset_dir}")
        
        print("✓ 后处理完成\n")
    
    def show_result(self):
        """显示打包结果"""
        print("=" * 60)
        print("打包完成!")
        print("=" * 60)
        
        exe_dir = self.dist_dir / self.app_name
        exe_path = exe_dir / f"{self.app_name}.exe"
        
        if exe_path.exists():
            # 计算整个目录的大小
            total_size = sum(f.stat().st_size for f in exe_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            print(f"\n可执行文件: {exe_path.relative_to(self.dist_dir)}")
            print(f"输出目录: {exe_dir}")
            print(f"总大小: {size_mb:.2f} MB")
            
            # 显示目录结构
            print(f"\n目录结构:")
            print(f"{self.app_name}/")
            print(f"├── {self.app_name}.exe           # 主程序")
            print(f"├── _internal/                    # 运行时依赖（不要删除）")
            print(f"│   └── assets/")
            print(f"│       └── presets/              # 预设图片（只读）")
            print(f"├── images/")
            print(f"│   └── custom/                   # 自定义图片（可写）")
            print(f"├── backup/                       # 备份目录（可写）")
            print(f"├── config.json                   # 配置文件（运行后生成）")
            # print(f"└── 运行说明.txt                  # 使用说明")
            
            print(f"\n分发说明:")
            print(f"  将整个 '{self.app_name}' 目录打包分发给用户")
            print(f"  用户只需解压后运行 {self.app_name}.exe 即可")
            
        else:
            print(f"\n✗ 未找到可执行文件: {exe_path}")
    
    def create_zip(self):
        """创建分发包"""
        print("\n" + "=" * 60)
        print("步骤 7: 创建分发包...")
        print("=" * 60)
        
        exe_dir = self.dist_dir / self.app_name
        
        if not exe_dir.exists():
            print("✗ 输出目录不存在，跳过")
            return
        
        try:
            zip_name = f"{self.app_name}_v1.0"
            zip_path = self.dist_dir / zip_name
            
            print(f"正在创建压缩包: {zip_name}.zip")
            shutil.make_archive(str(zip_path), 'zip', self.dist_dir, self.app_name)
            
            zip_file = Path(f"{zip_path}.zip")
            if zip_file.exists():
                size_mb = zip_file.stat().st_size / (1024 * 1024)
                print(f"✓ 压缩包创建成功: {zip_file}")
                print(f"  大小: {size_mb:.2f} MB")
            
        except Exception as e:
            print(f"⚠ 创建压缩包失败: {e}")
    
    def run(self):
        """运行完整构建流程"""
        print("\n" + "=" * 60)
        print(f"开始构建: {self.app_name}")
        print("模式: 目录模式（非单文件）")
        print("=" * 60 + "\n")
        
        try:
            self.clean()
            self.check_dependencies()
            self.build()
            self.post_build()
            self.show_result()
            self.create_zip()
            
            print("\n" + "=" * 60)
            print("构建流程全部完成! ✓")
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"\n✗ 构建失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    builder = Builder()
    builder.run()
