#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志管理器

提供日志记录和显示功能。
"""

import tkinter as tk
import time

class Logger:
    """日志管理器类"""
    
    def __init__(self, root):
        """初始化日志管理器"""
        self.root = root
        self.log_text = None  # 会在UI创建过程中设置
        
    def set_log_widget(self, log_text):
        """设置日志文本控件"""
        self.log_text = log_text
        
    def log(self, message):
        """记录日志消息"""
        if not self.log_text:
            print(f"日志控件未设置，消息：{message}")
            return
            
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        log_message = f"[{timestamp}] {message}"
        
        # 在UI线程中更新日志
        self.root.after(0, lambda: self._update_log_text(log_message))
        
        # 同时打印到控制台
        print(log_message)
        
    def _update_log_text(self, message):
        """更新日志文本控件"""
        self.log_text.config(state=tk.NORMAL)  # 允许修改
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到最后
        self.log_text.config(state=tk.DISABLED)  # 恢复只读 