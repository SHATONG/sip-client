#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置面板

包含PJSUA设置和端口配置。
"""

import tkinter as tk
from tkinter import ttk

class SettingsPanel:
    """设置面板类 - iOS风格"""
    
    def __init__(self, parent, client):
        """初始化设置面板 - iOS风格设计"""
        self.client = client
        self.parent = parent
        
        # 主容器
        main_container = ttk.Frame(parent, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # PJSUA 设置框架
        pjsua_section = ttk.LabelFrame(main_container, text="PJSUA设置", padding=15)
        pjsua_section.pack(fill=tk.X, pady=10)
        
        # PJSUA路径设置
        path_row = ttk.Frame(pjsua_section)
        path_row.pack(fill=tk.X, pady=8)
        
        ttk.Label(
            path_row, 
            text="PJSUA路径:", 
            font=('SF Pro Display', 11),
            foreground="#8E8E93"
        ).pack(side=tk.LEFT)
        
        # 创建PJSUA路径输入框
        self.pjsua_path_entry = ttk.Entry(path_row)
        # 自动查找可能的pjsua路径
        default_path = client.pjsua_utils.find_pjsua_path()
        self.pjsua_path_entry.insert(0, default_path)
        self.pjsua_path_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # 端口设置
        port_row = ttk.Frame(pjsua_section)
        port_row.pack(fill=tk.X, pady=8)
        
        ttk.Label(
            port_row, 
            text="本地端口:", 
            font=('SF Pro Display', 11),
            foreground="#8E8E93"
        ).pack(side=tk.LEFT)
        
        # 端口输入框
        port_frame = ttk.Frame(port_row)
        port_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.port_entry = ttk.Entry(port_frame, width=10)
        default_port = client.pjsua_utils.find_available_port(5070)
        self.port_entry.insert(0, str(default_port))
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        # 自动查找端口按钮
        self.auto_port_button = ttk.Button(
            port_frame, 
            text="自动查找", 
            command=self.auto_find_port, 
            width=8
        )
        self.auto_port_button.pack(side=tk.LEFT, padx=5)
        
        # 自动登录选项
        login_row = ttk.Frame(pjsua_section)
        login_row.pack(fill=tk.X, pady=8)
        
        self.auto_login_var = tk.BooleanVar(value=client.config_manager.get('auto_login', False))
        self.auto_login_check = ttk.Checkbutton(
            login_row, 
            text="启动时自动登录", 
            variable=self.auto_login_var,
            command=self.toggle_auto_login
        )
        self.auto_login_check.pack(side=tk.LEFT)
        
        # 工具按钮区域
        tools_section = ttk.LabelFrame(main_container, text="工具", padding=15)
        tools_section.pack(fill=tk.X, pady=10)
        
        # 工具按钮行
        tools_row = ttk.Frame(tools_section)
        tools_row.pack(fill=tk.X, pady=8)
        
        # PJSUA检查按钮
        self.check_pjsua_button = ttk.Button(
            tools_row, 
            text="检查PJSUA", 
            command=self.check_pjsua_handler
        )
        self.check_pjsua_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 浏览按钮
        self.browse_pjsua_button = ttk.Button(
            tools_row, 
            text="浏览", 
            command=self.browse_pjsua
        )
        self.browse_pjsua_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 下载按钮
        self.download_pjsua_button = ttk.Button(
            tools_row, 
            text="下载", 
            command=self.download_pjsua
        )
        self.download_pjsua_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 保存设置区域
        save_section = ttk.Frame(main_container, padding=10)
        save_section.pack(fill=tk.X, pady=10)
        
        # 保存设置按钮
        self.save_settings_button = ttk.Button(
            save_section, 
            text="保存设置", 
            command=self.save_settings
        )
        self.save_settings_button.pack(fill=tk.X, expand=True)
    
    def toggle_auto_login(self):
        """切换自动登录状态"""
        auto_login = self.auto_login_var.get()
        self.client.config_manager.set('auto_login', auto_login)
        self.client.config_manager.save_config()
        self.client.log(f"自动登录已{'启用' if auto_login else '禁用'}")
    
    def save_settings(self):
        """保存当前设置"""
        # 保存PJSUA路径和端口
        self.client.config_manager.set('pjsua_path', self.pjsua_path_entry.get())
        self.client.config_manager.set('port', int(self.port_entry.get()))
        self.client.config_manager.save_config()
        
        # 保存其他设置
        self.client.save_settings_to_config()
        
        self.client.log("设置已保存")
    
    def check_pjsua_handler(self):
        """处理检查PJSUA按钮点击事件"""
        if hasattr(self.client, 'sip_manager'):
            self.client.sip_manager.check_pjsua()
        else:
            path = self.pjsua_path_entry.get()
            self.client.pjsua_utils.check_pjsua(path)
        
    def browse_pjsua(self):
        """浏览选择PJSUA路径"""
        self.client.pjsua_utils.browse_pjsua(self.pjsua_path_entry)
        
    def download_pjsua(self):
        """下载PJSUA"""
        self.client.pjsua_utils.download_pjsua()
        
    def auto_find_port(self):
        """自动查找可用端口"""
        # 使用客户端的随机端口更新方法
        random_port = self.client.update_random_port()
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, str(random_port))
        self.client.log(f"已设置为随机端口: {random_port}") 