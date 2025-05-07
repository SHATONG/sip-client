#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
状态面板

显示SIP连接状态、账号信息和通话状态。
"""

import tkinter as tk
from tkinter import ttk

class StatusPanel:
    """状态显示面板 - iOS风格"""
    
    def __init__(self, parent):
        """初始化状态面板 - iOS风格设计"""
        # 状态区域 - iOS风格
        status_frame = ttk.Frame(parent, padding=15)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建iOS风格状态卡片
        status_box = ttk.LabelFrame(status_frame, text="连接状态", padding=15)
        status_box.pack(fill=tk.BOTH, expand=True)
        
        # 创建状态容器
        status_container = ttk.Frame(status_box)
        status_container.pack(fill=tk.X, padx=10, pady=5)
        
        # 使用更iOS风格的布局 - 垂直排列，每行都是一个分组
        # 连接状态行
        status_row = ttk.Frame(status_container)
        status_row.pack(fill=tk.X, pady=5)
        
        status_icon = tk.Canvas(status_row, width=15, height=15, bg="#F2F2F7", highlightthickness=0)
        status_icon.pack(side=tk.LEFT, padx=(0, 8))
        # 创建状态指示器（绿色圆点）
        self.status_indicator = status_icon.create_oval(2, 2, 13, 13, fill="red", outline="")
        
        ttk.Label(
            status_row, 
            text="连接状态:", 
            font=('SF Pro Display', 11),
            foreground="#8E8E93"
        ).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(
            status_row, 
            text="未连接", 
            foreground="red", 
            font=('SF Pro Display', 11, 'bold')
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # 分隔线
        separator1 = ttk.Separator(status_container, orient='horizontal')
        separator1.pack(fill=tk.X, pady=5)
        
        # 账号信息行
        account_row = ttk.Frame(status_container)
        account_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            account_row, 
            text="账号:", 
            font=('SF Pro Display', 11),
            foreground="#8E8E93"
        ).pack(side=tk.LEFT)
        
        self.account_label = ttk.Label(
            account_row, 
            text="无", 
            foreground="#8E8E93",
            font=('SF Pro Display', 11, 'bold')
        )
        self.account_label.pack(side=tk.RIGHT, padx=10)
        
        # 分隔线
        separator2 = ttk.Separator(status_container, orient='horizontal')
        separator2.pack(fill=tk.X, pady=5)
        
        # 通话状态行
        call_status_row = ttk.Frame(status_container)
        call_status_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            call_status_row, 
            text="通话状态:", 
            font=('SF Pro Display', 11),
            foreground="#8E8E93"
        ).pack(side=tk.LEFT)
        
        self.call_status_label = ttk.Label(
            call_status_row, 
            text="无通话", 
            foreground="#8E8E93",
            font=('SF Pro Display', 11, 'bold')
        )
        self.call_status_label.pack(side=tk.RIGHT, padx=10)
        
        # 分隔线
        separator3 = ttk.Separator(status_container, orient='horizontal')
        separator3.pack(fill=tk.X, pady=5)
        
        # 通话时间行
        call_time_row = ttk.Frame(status_container)
        call_time_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            call_time_row, 
            text="通话时间:", 
            font=('SF Pro Display', 11),
            foreground="#8E8E93"
        ).pack(side=tk.LEFT)
        
        self.call_time_label = ttk.Label(
            call_time_row, 
            text="00:00:00", 
            foreground="#8E8E93",
            font=('SF Pro Display', 11, 'bold')
        )
        self.call_time_label.pack(side=tk.RIGHT, padx=10)
        
    def update_status_indicator(self, color):
        """更新状态指示器颜色"""
        status_icon = self.status_label.master.winfo_children()[0]
        if isinstance(status_icon, tk.Canvas):
            status_icon.itemconfig(self.status_indicator, fill=color) 