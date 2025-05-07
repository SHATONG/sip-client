#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI管理器

负责界面的创建和管理。
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from gui.status_panel import StatusPanel
from gui.dial_panel import DialPanel
from gui.settings_panel import SettingsPanel

class UIManager:
    """管理应用程序的用户界面"""
    
    def __init__(self, root, client):
        """
        初始化UI管理器
        
        Args:
            root: Tkinter根窗口
            client: SIP客户端实例
        """
        self.root = root
        self.client = client
        
        # 设置主题和样式
        self.setup_styles()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=5)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        self.create_header()
        
        # 创建底部状态栏 - 放在标签页之前，确保优先显示
        self.status_bar = self.create_status_bar(self.main_frame)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 登录标签页
        self.login_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.login_tab, text="登录")
        
        # 拨号标签页
        self.dial_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dial_tab, text="拨号")
        
        # 键盘标签页 - 移除，合并到拨号页
        # self.keypad_tab = ttk.Frame(self.notebook)
        # self.notebook.add(self.keypad_tab, text="键盘")
        
        # 状态标签页 - 移除，改为底部状态栏
        # self.status_tab = ttk.Frame(self.notebook)
        # self.notebook.add(self.status_tab, text="状态")
        
        # 设置标签页
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="设置")
        
        # 日志标签页 - 新增
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="日志")
        
        # 创建登录面板 (放在登录标签页)
        self.server_panel = self.create_server_panel(self.login_tab)
        
        # 初始化拨号面板
        self.dial_panel = DialPanel(self.dial_tab, self.client)
        
        # 不再创建独立键盘面板
        # self.keypad_panel = self.dial_panel.create_standalone_keypad(self.keypad_tab)
        
        # 初始化设置面板 (放在设置标签页)
        self.settings_panel = SettingsPanel(self.settings_tab, self.client)
        
        # 创建日志面板 (放在日志标签页)
        self.log_panel = self.create_log_panel(self.log_tab)
        
        # 初始化状态
        self.update_status("未连接", "red")
        self.update_account_info("无", "gray")
        self.update_call_status("无通话", "gray")
        self.disable_dial_button()
        self.disable_hangup_button()
        
    def setup_styles(self):
        """设置样式和主题 - iOS风格"""
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        # iOS风格颜色
        bg_color = "#F2F2F7"  # iOS浅灰背景
        accent_color = "#007AFF"  # iOS蓝色
        green_color = "#34C759"  # iOS绿色
        red_color = "#FF3B30"  # iOS红色
        text_color = "#000000"  # 文本颜色
        secondary_text = "#8E8E93"  # 次要文本颜色
        
        # 设置窗口背景
        self.root.configure(background=bg_color)
        
        # 基本样式
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, font=('SF Pro Display', 10), foreground=text_color)
        
        # 标题样式
        self.style.configure('Header.TLabel', 
                             font=('SF Pro Display', 20, 'bold'), 
                             foreground=text_color,
                             background=bg_color)
        
        # 状态标签样式
        self.style.configure('Status.TLabel', 
                             font=('SF Pro Display', 12, 'bold'),
                             background=bg_color)
        
        # 按钮样式 - iOS风格圆角按钮
        self.style.configure('TButton', 
                             font=('SF Pro Display', 10, 'bold'),
                             background=accent_color, 
                             foreground="white",
                             borderwidth=0,
                             padding=10)
        
        # 标签框样式
        self.style.configure('TLabelframe', 
                             background=bg_color,
                             borderwidth=0,
                             relief="flat")
        
        self.style.configure('TLabelframe.Label', 
                             background=bg_color,
                             font=('SF Pro Display', 12, 'bold'),
                             foreground=text_color)
        
        # 输入框样式
        self.style.configure('TEntry', 
                            font=('SF Pro Display', 11),
                            fieldbackground='white',
                            borderwidth=1,
                            padding=8,
                            relief="solid")
        
        # 拨号和挂断按钮样式
        self.style.configure('Call.TButton', 
                            background=green_color,
                            foreground='white',
                            font=('SF Pro Display', 12, 'bold'),
                            padding=12)
        
        self.style.configure('Hangup.TButton', 
                            background=red_color,
                            foreground='white',
                            font=('SF Pro Display', 12, 'bold'),
                            padding=12)
        
        # 键盘按钮样式
        self.style.configure('Keypad.TButton', 
                            font=('SF Pro Display', 16, 'bold'),
                            padding=15,
                            background='white',
                            foreground=text_color)
        
        # 设置框架间距
        self.root.option_add('*padX', 10)
        self.root.option_add('*padY', 10)
        
    def create_header(self):
        """创建标题栏 - iOS风格"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # iOS风格标题居中
        header_label = ttk.Label(header_frame, text="SIP 电话", style='Header.TLabel')
        header_label.pack(side=tk.TOP, pady=15)
        
        # 添加一条分隔线
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
    def create_server_panel(self, parent):
        """创建服务器配置面板 - iOS风格"""
        server_frame = ttk.Frame(parent)
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用更iOS风格的布局
        server_container = ttk.Frame(server_frame, padding=10)
        server_container.pack(fill=tk.X)
        
        # 服务器信息行
        server_row = ttk.Frame(server_container)
        server_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            server_row, 
            text="SIP 服务器:", 
            font=('SF Pro Display', 11),
            width=12,
            foreground="#8E8E93"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.server_entry = ttk.Entry(server_row)
        self.server_entry.insert(0, "10.20.25.111")
        self.server_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 用户名行
        username_row = ttk.Frame(server_container)
        username_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            username_row, 
            text="用户名:", 
            font=('SF Pro Display', 11),
            width=12,
            foreground="#8E8E93"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.username_entry = ttk.Entry(username_row)
        self.username_entry.insert(0, "1000")
        self.username_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 密码行
        password_row = ttk.Frame(server_container)
        password_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            password_row, 
            text="密码:", 
            font=('SF Pro Display', 11),
            width=12,
            foreground="#8E8E93"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.password_entry = ttk.Entry(password_row, show="*")
        self.password_entry.insert(0, "1234")
        self.password_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 按钮容器
        button_frame = ttk.Frame(server_container, padding=(0, 10, 0, 0))
        button_frame.pack(fill=tk.X)
        
        # 登录按钮
        self.login_button = ttk.Button(
            button_frame, 
            text="登录", 
            command=lambda: self.client.sip_manager.login(
                self.server_entry.get(),
                self.username_entry.get(),
                self.password_entry.get()
            )
        )
        self.login_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 断开连接按钮 (原退出按钮)
        self.disconnect_button = ttk.Button(
            button_frame, 
            text="断开连接", 
            command=self.disconnect_sip
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.disconnect_button.state(['disabled'])  # 初始状态为禁用
        
        return server_frame
        
    def create_log_panel(self, parent):
        """创建日志显示面板 - 放在日志标签页"""
        log_frame = ttk.Frame(parent, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部控制区域
        controls_frame = ttk.Frame(log_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加日志下载按钮
        download_button = ttk.Button(
            controls_frame, 
            text="下载日志", 
            command=self.download_log
        )
        download_button.pack(side=tk.RIGHT, padx=5)
        
        # 添加清除日志按钮
        clear_button = ttk.Button(
            controls_frame, 
            text="清除日志", 
            command=self.clear_log
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建带滚动条的日志文本区域
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            wrap=tk.WORD, 
            height=20,  # 增加高度
            background='#f8f8f8',
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # 设置为只读
        
        # 设置日志控件到logger
        self.client.logger.set_log_widget(self.log_text)
        
        return log_frame
        
    def create_status_bar(self, parent):
        """创建底部状态栏，显示为单行"""
        # 创建状态栏框架
        status_bar = ttk.Frame(parent)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 2))
        
        # 添加分隔线
        separator = ttk.Separator(status_bar, orient='horizontal')
        separator.pack(fill=tk.X, pady=2)
        
        # 主状态容器 - 使用表格式布局
        main_status = ttk.Frame(status_bar)
        main_status.pack(fill=tk.X, padx=5, pady=2)
        
        # 使用表格布局，确保所有元素对齐
        # 状态指示灯
        status_icon = tk.Canvas(main_status, width=12, height=12, bg="#F2F2F7", highlightthickness=0)
        status_icon.grid(row=0, column=0, padx=(0, 2))
        self.status_indicator = status_icon.create_oval(2, 2, 10, 10, fill="red", outline="")
        
        # 连接状态标签
        self.status_label = ttk.Label(
            main_status, 
            text="未连接", 
            font=('SF Pro Display', 9, 'bold'),
            width=8,
            foreground="red"
        )
        self.status_label.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        # 账号标签
        ttk.Label(
            main_status, 
            text="账号:", 
            font=('SF Pro Display', 9),
            width=5,
            foreground="#8E8E93"
        ).grid(row=0, column=2, sticky='e')
        
        # 账号值
        self.account_label = ttk.Label(
            main_status, 
            text="无", 
            font=('SF Pro Display', 9, 'bold'),
            width=30,  # 固定宽度，确保足够显示长账号
            anchor='w',
            foreground="gray"
        )
        self.account_label.grid(row=0, column=3, sticky='w', padx=(5, 20))
        
        # 通话标签
        ttk.Label(
            main_status, 
            text="通话:", 
            font=('SF Pro Display', 9),
            width=5,
            foreground="#8E8E93"
        ).grid(row=0, column=4, sticky='e')
        
        # 通话状态
        self.call_status_label = ttk.Label(
            main_status, 
            text="无通话", 
            font=('SF Pro Display', 9, 'bold'),
            width=8,
            anchor='w',
            foreground="gray"
        )
        self.call_status_label.grid(row=0, column=5, sticky='w', padx=(5, 10))
        
        # 通话时间
        self.call_time_label = ttk.Label(
            main_status, 
            text="00:00:00", 
            font=('SF Pro Display', 9, 'bold'),
            width=8,
            anchor='e',
            foreground="gray"
        )
        self.call_time_label.grid(row=0, column=6, sticky='e', padx=(0, 5))
        
        # 配置列权重，使中间的账号区域可以自动扩展
        main_status.columnconfigure(3, weight=1)
        
        return status_bar
        
    # 状态更新相关方法
    def update_status(self, status_text, color):
        """更新连接状态"""
        self.status_label.config(text=status_text, foreground=color)
        # 更新状态指示器颜色
        if hasattr(self, 'status_indicator'):
            self.status_label.master.winfo_children()[0].itemconfig(self.status_indicator, fill=color)
        
    def update_account_info(self, account_text, color):
        """更新账号信息"""
        self.account_label.config(text=account_text, foreground=color)
        
    def update_call_status(self, status_text, color):
        """更新通话状态"""
        self.call_status_label.config(text=status_text, foreground=color)
        
    def update_call_time(self, time_text, color="blue"):
        """更新通话时间"""
        self.call_time_label.config(text=time_text, foreground=color)
        
    def enable_dial_button(self):
        """启用拨号按钮"""
        self.dial_panel.dial_button.state(['!disabled'])
        
    def disable_dial_button(self):
        """禁用拨号按钮"""
        self.dial_panel.dial_button.state(['disabled'])
        
    def enable_hangup_button(self):
        """启用挂断按钮"""
        self.dial_panel.hangup_button.state(['!disabled'])
        
    def disable_hangup_button(self):
        """禁用挂断按钮"""
        self.dial_panel.hangup_button.state(['disabled'])
        
    def enable_login_button(self):
        """启用登录按钮"""
        self.login_button.state(['!disabled'])
        
    def disable_login_button(self):
        """禁用登录按钮"""
        self.login_button.state(['disabled'])
        
    def set_login_button_connected(self):
        """设置登录按钮为已连接状态"""
        self.login_button.config(text="已连接")
        self.login_button.state(['disabled'])
        
    def reset_login_button(self):
        """重置登录按钮为初始状态"""
        self.login_button.config(text="登录")
        self.login_button.state(['!disabled'])
        
    def get_server_info(self):
        """获取服务器信息"""
        return {
            'server': self.server_entry.get(),
            'username': self.username_entry.get(),
            'password': self.password_entry.get()
        }
        
    def get_dial_number(self):
        """获取拨号号码"""
        return self.dial_panel.dial_entry.get()
        
    def get_port(self):
        """获取端口号"""
        return self.settings_panel.port_entry.get()
        
    def get_pjsua_path(self):
        """获取PJSUA路径"""
        return self.settings_panel.pjsua_path_entry.get()
        
    def download_log(self):
        """下载日志到文件"""
        try:
            # 获取当前时间戳作为文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sip_client_log_{timestamp}.txt"
            
            # 打开保存文件对话框
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                initialfile=filename
            )
            
            if not filepath:
                return  # 用户取消操作
                
            # 保存日志内容到文件
            log_content = self.log_text.get(1.0, tk.END)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(log_content)
                
            messagebox.showinfo("成功", f"日志已保存到: {filepath}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存日志时出错: {str(e)}")
            
    def clear_log(self):
        """清除日志内容"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.client.logger.log("日志已清除")
        
    def disconnect_sip(self):
        """断开SIP连接"""
        if hasattr(self.client, 'sip_manager'):
            # 调用SIP管理器的注销方法
            self.client.sip_manager.unregister()
            
            # 更新UI状态
            self.update_status("已断开", "red")
            self.update_account_info("无", "gray")
            
            # 启用登录按钮，禁用断开按钮
            self.enable_login_button()
            self.disable_disconnect_button()
            
            # 禁用拨号按钮
            self.disable_dial_button()
            
    def enable_disconnect_button(self):
        """启用断开连接按钮"""
        self.disconnect_button.state(['!disabled'])
        
    def disable_disconnect_button(self):
        """禁用断开连接按钮"""
        self.disconnect_button.state(['disabled']) 