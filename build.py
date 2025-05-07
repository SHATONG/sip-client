#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打包脚本 - 将SIP客户端打包成可执行文件
使用PyInstaller将项目打包成单一的exe文件
"""

import os
import sys
import shutil
import subprocess
import platform
import time

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name} 目录")
    
    # 删除spec文件
    spec_file = "SIPClient.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"已删除 {spec_file} 文件")
    
    # 删除__pycache__目录
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"已删除 {pycache_path} 目录")

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("PyInstaller 已安装")
        return True
    except ImportError:
        print("PyInstaller 未安装. 正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller 安装成功")
            return True
        except Exception as e:
            print(f"安装 PyInstaller 失败: {str(e)}")
            return False

def get_hidden_imports():
    """获取需要包含的隐藏导入"""
    # 添加可能未被自动检测到的模块
    hidden_imports = [
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "json",
        "socket",
        "random",
        "subprocess",
        "webbrowser",
        "time",
        "threading",
        "re",
        "os",
        "sys",
        "traceback"
    ]
    
    # 添加项目模块
    project_modules = [
        "core",
        "gui",
        "utils",
        "core.pjsua_utils",
        "core.sip_manager",
        "gui.ui_manager",
        "gui.status_panel",
        "gui.dial_panel",
        "gui.settings_panel",
        "utils.logger",
        "utils.config_manager"
    ]
    
    hidden_imports.extend(project_modules)
    return hidden_imports

def collect_data_files():
    """收集需要包含的数据文件"""
    data_files = []
    
    # 添加配置文件
    if os.path.exists("sip_client_config.json"):
        data_files.append(("sip_client_config.json", "."))
    
    # 添加PJSUA可执行文件
    if os.path.exists("pjsua.exe"):
        data_files.append(("pjsua.exe", "."))
    
    # 添加图标文件(如果存在)
    if os.path.exists("phone.ico"):
        data_files.append(("phone.ico", "."))
    
    return data_files

def check_requirements():
    """检查并安装依赖库"""
    print("检查依赖库...")
    
    # 列出项目所需的库
    required_packages = [
        "pillow",  # 用于图像处理
    ]
    
    for package in required_packages:
        try:
            __import__(package.lower())
            print(f"{package} 已安装")
        except ImportError:
            print(f"{package} 未安装，正在安装...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                print(f"{package} 安装成功")
            except Exception as e:
                print(f"安装 {package} 失败: {str(e)}")
                print("警告: 打包过程可能会因缺少此依赖而失败")
    
    return True

def build_exe():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 获取隐藏导入
    hidden_imports = get_hidden_imports()
    
    # 获取数据文件
    data_files = collect_data_files()
    
    # 设置基本PyInstaller命令行参数
    pyinstaller_args = [
        "main.py",                   # 主脚本
        "--name=SIPClient",          # 输出文件名
        "--onefile",                 # 单文件模式
        "--windowed",                # 无控制台窗口
        "--clean",                   # 清理临时文件
        "--noconfirm",               # 不显示确认对话框
    ]
    
    # 添加图标(如果存在)
    if os.path.exists("phone.ico"):
        pyinstaller_args.append("--icon=phone.ico")
    
    # 添加隐藏导入
    for module in hidden_imports:
        pyinstaller_args.append(f"--hidden-import={module}")
    
    # 添加数据文件
    for src, dest in data_files:
        if platform.system() == 'Windows':
            separator = ";"
        else:
            separator = ":"
        pyinstaller_args.append(f"--add-data={src}{separator}{dest}")
    
    # 执行PyInstaller命令
    try:
        print("\n======= 构建命令 =======")
        print("python -m PyInstaller " + " ".join(pyinstaller_args))
        print("=========================\n")
        
        subprocess.run([sys.executable, "-m", "PyInstaller"] + pyinstaller_args, check=True)
        
        print("\n构建成功! 可执行文件位于 dist/SIPClient.exe")
        print("您可以直接运行该文件使用SIP客户端")
        
        # 在资源管理器中打开dist目录
        if platform.system() == 'Windows':
            os.startfile(os.path.abspath("dist"))
        
    except Exception as e:
        print(f"构建失败: {str(e)}")

def info_header():
    """打印信息头"""
    print("\n" + "=" * 60)
    print("  SIP客户端打包工具  ".center(60))
    print("=" * 60)
    print(f"操作系统: {platform.system()} {platform.version()}")
    print(f"Python版本: {platform.python_version()}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    # 显示信息头
    info_header()
    
    # 检查是否为Windows系统
    if platform.system() != 'Windows':
        print("警告: 此脚本设计用于Windows系统，在其他系统上可能无法正常工作")
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 检查并安装依赖库
    if check_requirements():
        # 检查并安装PyInstaller
        if check_pyinstaller():
            # 构建可执行文件
            build_exe()
    
    print("\n======= 打包过程完成 =======")
    print("如果成功，请在dist目录中找到SIPClient.exe文件")
    
    # 在Windows上暂停，避免立即关闭窗口
    if platform.system() == 'Windows':
        input("\n按回车键退出...") 