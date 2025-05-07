#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PJSUA工具类

提供与PJSUA相关的辅助功能。
"""

import os
import socket
import random
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

class PJSUAUtils:
    """PJSUA辅助工具类"""
    
    def __init__(self, logger):
        """初始化PJSUA工具类"""
        self.logger = logger
        
    def find_pjsua_path(self):
        """尝试自动查找pjsua可能的路径"""
        # 默认路径
        default_path = "pjsua.exe"
        
        # 检查当前目录
        current_dir_path = os.path.join(os.getcwd(), "pjsua.exe")
        if os.path.exists(current_dir_path):
            return current_dir_path
            
        # 检查可能的安装目录
        possible_paths = [
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), "PJSIP", "bin", "pjsua.exe"),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), "PJSIP", "bin", "pjsua.exe"),
            os.path.join(os.environ.get('USERPROFILE', 'C:\\Users\\Default'), "Downloads", "pjsua.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return default_path
        
    def browse_pjsua(self, path_entry):
        """浏览并选择pjsua.exe路径"""
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="选择pjsua.exe文件",
            filetypes=(("可执行文件", "*.exe"), ("所有文件", "*.*"))
        )
        if filename:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, filename)
            
    def download_pjsua(self):
        """打开PJSIP下载页面"""
        download_url = "https://www.pjsip.org/download.htm"
        download_msg = """
PJSUA下载和安装指南:

1. 访问PJSIP官网下载页面
2. 下载最新版本的源代码
3. 按照官方文档编译安装
4. 将pjsua.exe放置在系统PATH中

或者:
1. 搜索"pjsua.exe download"寻找预编译版本
2. 下载后放置在当前目录

是否打开PJSIP下载页面?
        """
        if messagebox.askyesno("下载PJSUA", download_msg):
            webbrowser.open(download_url)
            
    def check_pjsua(self, pjsua_path):
        """检查PJSUA是否可用"""
        try:
            # 检查路径是否存在
            if not os.path.exists(pjsua_path):
                self.logger.log(f"PJSUA路径不存在: {pjsua_path}")
                messagebox.showerror("PJSUA检测失败", 
                    f"找不到PJSUA可执行文件: {pjsua_path}\n\n您需要下载并安装PJSUA才能连接到SIP服务器。")
                return False
                
            # 尝试运行pjsua --help看是否工作
            result = subprocess.run([pjsua_path, "--help"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   shell=True,
                                   timeout=2)
            if "Usage:" in result.stdout or "pjsua" in result.stdout:
                self.logger.log(f"PJSUA检测成功: {pjsua_path}")
                return True
            else:
                self.logger.log(f"PJSUA似乎不工作: {result.stderr}")
                messagebox.showerror("PJSUA检测失败", 
                    f"PJSUA找到了，但无法正常运行。\n错误信息: {result.stderr}")
                return False
        except Exception as e:
            self.logger.log(f"PJSUA检测失败: {str(e)}")
            messagebox.showerror("PJSUA检测失败", 
                f"PJSUA检测时出错: {str(e)}\n\n您需要下载并安装PJSUA才能连接到SIP服务器。")
            return False
            
    def find_available_port(self, start_port=5060):
        """查找可用的SIP端口"""
        # 直接生成随机端口
        port = random.randint(10000, 60000)
        self.logger.log(f"生成随机端口: {port}")
        
        # 尝试测试随机端口是否可用
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('0.0.0.0', port))
            s.close()
            self.logger.log(f"随机端口 {port} 可用")
            return port
        except:
            # 如果随机端口不可用，再次尝试
            self.logger.log(f"随机端口 {port} 不可用，重新生成")
            port = random.randint(10000, 60000)
            self.logger.log(f"重新生成随机端口: {port}")
            return port 