#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SIP客户端主类

包含SIP客户端的核心逻辑和GUI设置。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import sys
import traceback

from gui.ui_manager import UIManager
from core.sip_manager import SIPManager
from core.pjsua_utils import PJSUAUtils
from utils.logger import Logger
from utils.config_manager import ConfigManager

class SIPClient:
    """SIP客户端主类，整合UI和SIP功能"""
    
    def __init__(self):
        """初始化SIP客户端"""
        try:
            # 设置全局异常处理
            sys.excepthook = self.handle_exception
            
            # 创建窗口
            self.root = tk.Tk()
            self.root.title("SIP 电话")  # 简化标题
            self.root.geometry("500x700")  # 适合标签页布局的尺寸
            self.root.resizable(True, True)
            
            # 设置应用图标（如果有的话）
            try:
                self.root.iconbitmap("phone.ico")  # 如果有图标文件的话
            except:
                pass
            
            # 初始化配置管理器
            self.config_manager = ConfigManager()
            
            # 初始化日志管理器
            self.logger = Logger(self.root)
            
            # 初始化PJSUA工具 (必须在UI管理器之前初始化)
            self.pjsua_utils = PJSUAUtils(self.logger)
            
            # 初始化UI管理器
            self.ui_manager = UIManager(self.root, self)
            
            # 确保UI管理器的日志文本框已设置
            self.logger.set_log_widget(self.ui_manager.log_text)
            
            # 初始化SIP管理器
            self.sip_manager = SIPManager(self, self.ui_manager, self.logger, self.pjsua_utils)
            
            # 从配置中加载UI设置
            self.load_settings_from_config()
            
            # 为窗口关闭事件绑定处理函数
            self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
            
            # 启动时自动检查PJSUA (使用延迟启动确保所有组件已初始化)
            self.root.after(500, self.delayed_startup)
        except Exception as e:
            messagebox.showerror("初始化错误", f"应用程序初始化失败: {str(e)}")
            raise
    
    def load_settings_from_config(self):
        """从配置加载设置到UI"""
        # 服务器设置
        if hasattr(self.ui_manager, 'server_entry'):
            self.ui_manager.server_entry.delete(0, tk.END)
            self.ui_manager.server_entry.insert(0, self.config_manager.get('server', '10.20.25.111'))
            
        if hasattr(self.ui_manager, 'username_entry'):
            self.ui_manager.username_entry.delete(0, tk.END)
            self.ui_manager.username_entry.insert(0, self.config_manager.get('username', '1000'))
            
        if hasattr(self.ui_manager, 'password_entry'):
            self.ui_manager.password_entry.delete(0, tk.END)
            self.ui_manager.password_entry.insert(0, self.config_manager.get('password', '1234'))
            
        # PJSUA设置
        if hasattr(self.ui_manager.settings_panel, 'pjsua_path_entry'):
            self.ui_manager.settings_panel.pjsua_path_entry.delete(0, tk.END)
            self.ui_manager.settings_panel.pjsua_path_entry.insert(0, self.config_manager.get('pjsua_path', 'pjsua.exe'))
            
        if hasattr(self.ui_manager.settings_panel, 'port_entry'):
            self.ui_manager.settings_panel.port_entry.delete(0, tk.END)
            self.ui_manager.settings_panel.port_entry.insert(0, str(self.config_manager.get('port', 5070)))
    
    def save_settings_to_config(self):
        """保存UI设置到配置"""
        # 获取服务器设置
        if hasattr(self.ui_manager, 'server_entry'):
            server = self.ui_manager.server_entry.get()
            username = self.ui_manager.username_entry.get()
            password = self.ui_manager.password_entry.get()
            
            # 获取PJSUA设置
            pjsua_path = self.ui_manager.settings_panel.pjsua_path_entry.get()
            port = self.ui_manager.settings_panel.port_entry.get()
            
            # 更新配置
            self.config_manager.update({
                'server': server,
                'username': username,
                'password': password,
                'pjsua_path': pjsua_path,
                'port': port
            })
            
            # 保存配置
            self.config_manager.save_config()
            
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        # 记录异常到日志
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.log(f"发生未捕获的异常: {error_msg}")
        
        # 显示错误消息框
        messagebox.showerror("应用程序错误", f"发生错误: {str(exc_value)}\n\n请查看日志获取详细信息。")
        
        # 调用原始的异常处理程序
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def log(self, message):
        """记录日志"""
        self.logger.log(message)
    
    def on_exit(self):
        """退出程序时清理资源"""
        try:
            # 保存配置
            self.save_settings_to_config()
            
            # 清理SIP资源
            self.sip_manager.cleanup()
            
            # 销毁窗口
            self.root.destroy()
        except Exception as e:
            self.logger.log(f"退出时出错: {str(e)}")
            self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.log(f"应用程序运行时出错: {str(e)}")
            raise
    
    def update_random_port(self):
        """更新为随机端口"""
        random_port = self.pjsua_utils.find_available_port()
        
        # 更新UI中的端口显示
        if hasattr(self.ui_manager.settings_panel, 'port_entry'):
            self.ui_manager.settings_panel.port_entry.delete(0, tk.END)
            self.ui_manager.settings_panel.port_entry.insert(0, str(random_port))
        
        # 更新配置
        self.config_manager.set('port', random_port)
        self.config_manager.save_config()
        
        self.logger.log(f"已设置为随机端口: {random_port}")
        return random_port
        
    def delayed_startup(self):
        """延迟启动，确保所有组件已初始化"""
        try:
            # 更新为随机端口
            self.update_random_port()
            
            # 检查PJSUA
            self.sip_manager.check_pjsua()
            
            # 如果配置了自动登录，则尝试登录
            if self.config_manager.get('auto_login', False):
                self.logger.log("正在尝试自动登录...")
                server = self.config_manager.get('server')
                username = self.config_manager.get('username')
                password = self.config_manager.get('password')
                
                if server and username and password:
                    self.sip_manager.login(server, username, password)
        except Exception as e:
            self.logger.log(f"启动时出错: {str(e)}")
            messagebox.showwarning("启动警告", f"启动过程中出现问题: {str(e)}") 