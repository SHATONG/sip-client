#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
拨号面板

包含拨号输入框、数字键盘和拨号控制按钮。
"""

import tkinter as tk
from tkinter import ttk

class DialPanel:
    """拨号面板类"""
    
    def __init__(self, parent, client):
        """初始化拨号面板"""
        self.client = client
        
        # 拨号区域 - iOS风格
        dial_frame = ttk.Frame(parent, padding=10)
        dial_frame.pack(fill=tk.BOTH, expand=True)
        
        # 拨号输入框 - 大字体，居中显示，iOS风格
        dial_input_frame = ttk.Frame(dial_frame)
        dial_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 添加大号字体的输入框
        self.dial_entry = ttk.Entry(
            dial_input_frame, 
            width=30, 
            font=('SF Pro Display', 24, 'bold'),
            justify='center'
        )
        self.dial_entry.insert(0, "1003")  # 默认号码
        self.dial_entry.pack(fill=tk.X, padx=20, pady=10)
        
        # 拨号按钮 - iOS风格圆形按钮，移到键盘之前
        dial_buttons = ttk.Frame(dial_frame, padding=(0, 5, 0, 10))
        dial_buttons.pack(fill=tk.X)
        
        # 拨打按钮 - 绿色圆形，iOS风格
        self.dial_button = ttk.Button(
            dial_buttons, 
            text="拨打", 
            command=self.make_call,
            width=15, 
            style='Call.TButton'
        )
        self.dial_button.pack(side=tk.LEFT, padx=15, pady=5, expand=True, fill=tk.X)
        self.dial_button.state(['disabled'])
        
        # 挂断按钮 - 红色圆形，iOS风格
        self.hangup_button = ttk.Button(
            dial_buttons, 
            text="挂断", 
            command=self.hangup,
            width=15, 
            style='Hangup.TButton'
        )
        self.hangup_button.pack(side=tk.RIGHT, padx=15, pady=5, expand=True, fill=tk.X)
        
        # 添加iOS风格数字键盘 - 放在按钮之后
        self.create_keypad(dial_frame)
        
    def create_keypad(self, parent):
        """创建iOS风格数字键盘"""
        keypad_frame = ttk.Frame(parent, padding=(5, 5, 5, 5))
        keypad_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建一个居中的容器
        keypad_container = ttk.Frame(keypad_frame)
        keypad_container.pack(expand=True)
        
        # 创建数字键盘按钮 - iOS风格
        keypad_buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '*', '0', '#'
        ]
        
        # 为美观起见，添加子标签
        keypad_sublabels = {
            '1': '', '2': 'ABC', '3': 'DEF',
            '4': 'GHI', '5': 'JKL', '6': 'MNO',
            '7': 'PQRS', '8': 'TUV', '9': 'WXYZ',
            '*': '', '0': '+', '#': ''
        }
        
        # 创建3x4的键盘布局 - iOS风格圆形按钮，使用更大的间距
        for i, button in enumerate(keypad_buttons):
            row = i // 3
            col = i % 3
            
            # 创建按钮框架以容纳按钮和子标签
            btn_frame = ttk.Frame(keypad_container)
            btn_frame.grid(row=row, column=col, padx=15, pady=10)  # 增加间距
            
            # 创建iOS风格的圆形按钮效果
            btn = tk.Button(
                btn_frame,
                text=button,
                font=('SF Pro Display', 18, 'bold'),
                width=3,  # 增加宽度
                height=1,
                relief='flat',
                bg='white',
                fg='black',
                bd=0,
                command=lambda d=button: self.add_digit(d)
            )
            btn.pack(side=tk.TOP, pady=(0, 2))
            
            # 添加子标签
            if keypad_sublabels[button]:
                sublabel = ttk.Label(
                    btn_frame,
                    text=keypad_sublabels[button],
                    font=('SF Pro Display', 7),
                    foreground="gray"
                )
                sublabel.pack(side=tk.TOP)
        
        # 添加清除按钮 - iOS风格
        clear_frame = ttk.Frame(keypad_frame)
        clear_frame.pack(fill=tk.X, pady=5)
        
        clear_btn = tk.Button(
            clear_frame,
            text="清除",
            font=('SF Pro Display', 12),
            fg='#007AFF',
            bg='white',
            relief='flat',
            bd=0,
            command=self.clear_dial
        )
        clear_btn.pack(pady=5, padx=50, fill=tk.X)
        
    def add_digit(self, digit):
        """添加数字到拨号输入框"""
        current = self.dial_entry.get()
        self.dial_entry.delete(0, tk.END)
        self.dial_entry.insert(0, current + digit)
        
    def clear_dial(self):
        """清除拨号输入框"""
        self.dial_entry.delete(0, tk.END)
        
    def make_call(self):
        """拨打电话"""
        self.client.sip_manager.make_call()
        
    def hangup(self):
        """挂断电话"""
        self.client.sip_manager.hangup() 
        
    def create_standalone_keypad(self, parent):
        """创建独立的键盘面板"""
        keypad_frame = ttk.Frame(parent, padding=(5, 5, 5, 5))
        keypad_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建一个居中的容器
        keypad_container = ttk.Frame(keypad_frame)
        keypad_container.pack(expand=True)
        
        # 创建数字键盘按钮 - iOS风格
        keypad_buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '*', '0', '#'
        ]
        
        # 为美观起见，添加子标签
        keypad_sublabels = {
            '1': '', '2': 'ABC', '3': 'DEF',
            '4': 'GHI', '5': 'JKL', '6': 'MNO',
            '7': 'PQRS', '8': 'TUV', '9': 'WXYZ',
            '*': '', '0': '+', '#': ''
        }
        
        # 创建3x4的键盘布局 - iOS风格圆形按钮，使用更大的间距
        for i, button in enumerate(keypad_buttons):
            row = i // 3
            col = i % 3
            
            # 创建按钮框架以容纳按钮和子标签
            btn_frame = ttk.Frame(keypad_container)
            btn_frame.grid(row=row, column=col, padx=15, pady=10)  # 增加间距
            
            # 创建iOS风格的圆形按钮效果
            btn = tk.Button(
                btn_frame,
                text=button,
                font=('SF Pro Display', 18, 'bold'),
                width=3,  # 增加宽度
                height=1,
                relief='flat',
                bg='white',
                fg='black',
                bd=0,
                command=lambda d=button: self.add_digit(d)
            )
            btn.pack(side=tk.TOP, pady=(0, 2))
            
            # 添加子标签
            if keypad_sublabels[button]:
                sublabel = ttk.Label(
                    btn_frame,
                    text=keypad_sublabels[button],
                    font=('SF Pro Display', 7),
                    foreground="gray"
                )
                sublabel.pack(side=tk.TOP)
        
        # 添加清除按钮 - iOS风格
        clear_frame = ttk.Frame(keypad_frame)
        clear_frame.pack(fill=tk.X, pady=5)
        
        clear_btn = tk.Button(
            clear_frame,
            text="清除",
            font=('SF Pro Display', 12),
            fg='#007AFF',
            bg='white',
            relief='flat',
            bd=0,
            command=self.clear_dial
        )
        clear_btn.pack(pady=5, padx=50, fill=tk.X)
        
        return keypad_frame 