import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import subprocess
import os
import re
import webbrowser
import sys
import socket
import random

class SIPClientTk:
    def __init__(self):
        self.call_in_progress = False
        self.is_connected = False
        self.process = None
        self.call_start_time = None
        self.call_timer_id = None
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("SIP 电话 ")
        self.root.geometry("700x900")
        self.root.resizable(True, True)
        
        # 设置主题和样式
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        # 定义自定义颜色和样式
        bg_color = "#f5f5f5"
        self.root.configure(background=bg_color)
        
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Status.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('TLabelframe', background=bg_color)
        self.style.configure('TLabelframe.Label', background=bg_color, font=('Arial', 11, 'bold'))
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        header_label = ttk.Label(header_frame, text="SIP 电话客户端", style='Header.TLabel')
        header_label.pack(side=tk.LEFT)
        
        # 服务器信息区域
        server_frame = ttk.LabelFrame(main_frame, text="服务器信息", padding=10)
        server_frame.pack(fill=tk.X, pady=8)
        
        server_grid = ttk.Frame(server_frame)
        server_grid.pack(fill=tk.X, padx=5)
        
        ttk.Label(server_grid, text="SIP 服务器:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.server_entry = ttk.Entry(server_grid, width=30)
        self.server_entry.insert(0, "10.20.25.111")
        self.server_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        ttk.Label(server_grid, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.username_entry = ttk.Entry(server_grid, width=30)
        self.username_entry.insert(0, "1000")  # 默认FreeSWITCH用户名
        self.username_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        ttk.Label(server_grid, text="密码:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.password_entry = ttk.Entry(server_grid, width=30, show="*")
        self.password_entry.insert(0, "1234")  # 默认FreeSWITCH密码
        self.password_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # 列配置，使条目可以扩展
        server_grid.columnconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(server_frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill=tk.X)
        
        self.login_button = ttk.Button(button_frame, text="登录", command=self.login, width=12)
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = ttk.Button(button_frame, text="退出", command=self.on_exit, width=12)
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # 拨号区域
        dial_frame = ttk.LabelFrame(main_frame, text="拨号", padding=10)
        dial_frame.pack(fill=tk.X, pady=8)
        
        dial_grid = ttk.Frame(dial_frame)
        dial_grid.pack(fill=tk.X, padx=5)
        
        ttk.Label(dial_grid, text="拨打电话:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.dial_entry = ttk.Entry(dial_grid, width=30)
        self.dial_entry.insert(0, "1003")  # 另一个FreeSWITCH分机
        self.dial_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # 列配置，使条目可以扩展
        dial_grid.columnconfigure(1, weight=1)
        
        # 添加数字键盘
        keypad_frame = ttk.Frame(dial_frame, padding=(0, 10, 0, 0))
        keypad_frame.pack(fill=tk.X)
        
        # 创建数字键盘按钮
        keypad_buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '*', '0', '#'
        ]
        
        # 添加数字到输入框的函数
        def add_digit(digit):
            current = self.dial_entry.get()
            self.dial_entry.delete(0, tk.END)
            self.dial_entry.insert(0, current + digit)
        
        # 创建3x4的键盘布局
        row, col = 0, 0
        for button in keypad_buttons:
            btn = ttk.Button(keypad_frame, text=button, width=5, 
                           command=lambda d=button: add_digit(d))
            btn.grid(row=row, column=col, padx=3, pady=3)
            col += 1
            if col > 2:  # 每行3个按钮
                col = 0
                row += 1
        
        # 添加清除按钮
        def clear_dial():
            self.dial_entry.delete(0, tk.END)
            
        clear_btn = ttk.Button(keypad_frame, text="清除", width=8, command=clear_dial)
        clear_btn.grid(row=row+1, column=0, columnspan=3, padx=3, pady=3, sticky=tk.EW)
        
        dial_buttons = ttk.Frame(dial_frame, padding=(0, 10, 0, 0))
        dial_buttons.pack(fill=tk.X)
        
        self.style.configure('Call.TButton', background='#4CAF50', foreground='white')
        self.style.configure('Hangup.TButton', background='#F44336', foreground='white')
        
        self.dial_button = ttk.Button(dial_buttons, text="拨打", command=self.make_call, width=12, style='Call.TButton')
        self.dial_button.pack(side=tk.LEFT, padx=5)
        self.dial_button.state(['disabled'])
        
        self.hangup_button = ttk.Button(dial_buttons, text="挂断", command=self.hangup, width=12, style='Hangup.TButton')
        self.hangup_button.pack(side=tk.LEFT, padx=5)
        self.hangup_button.state(['disabled'])
        
        # 状态区域
        status_frame = ttk.Frame(main_frame, padding=(0, 5, 0, 5))
        status_frame.pack(fill=tk.X, pady=5)
        
        # 创建更详细的状态显示
        status_box = ttk.LabelFrame(status_frame, text="连接状态", padding=5)
        status_box.pack(fill=tk.X)
        
        # 创建状态网格
        status_grid = ttk.Frame(status_box)
        status_grid.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_grid, text="连接状态:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.status_label = ttk.Label(status_grid, text="未连接", foreground="red", style='Status.TLabel')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(status_grid, text="账号:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.account_label = ttk.Label(status_grid, text="无", foreground="gray")
        self.account_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(status_grid, text="通话状态:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.call_status_label = ttk.Label(status_grid, text="无通话", foreground="gray")
        self.call_status_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # 在状态网格中添加通话时间显示
        ttk.Label(status_grid, text="通话时间:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.call_time_label = ttk.Label(status_grid, text="00:00:00", foreground="gray")
        self.call_time_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        # 创建带滚动条的日志文本区域
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            wrap=tk.WORD, 
            height=15,
            background='#f8f8f8',
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # 设置为只读
        
        # PJSUA 路径设置
        pjsua_frame = ttk.LabelFrame(main_frame, text="PJSUA设置", padding=10)
        pjsua_frame.pack(fill=tk.X, pady=8)
        
        pjsua_grid = ttk.Frame(pjsua_frame)
        pjsua_grid.pack(fill=tk.X, padx=5)
        
        ttk.Label(pjsua_grid, text="PJSUA路径:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.pjsua_path_entry = ttk.Entry(pjsua_grid, width=40)
        
        # 自动查找可能的pjsua路径
        default_path = self.find_pjsua_path()
        self.pjsua_path_entry.insert(0, default_path)
        self.pjsua_path_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=5)
        
        # 列配置，使条目可以扩展
        pjsua_grid.columnconfigure(1, weight=1)
        
        # 添加端口配置
        ttk.Label(pjsua_grid, text="本地端口:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.port_entry = ttk.Entry(pjsua_grid, width=10)
        default_port = self.find_available_port(5070)  # 从5070开始查找可用端口
        self.port_entry.insert(0, str(default_port))
        self.port_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 检查PJSUA是否存在
        pjsua_buttons = ttk.Frame(pjsua_frame, padding=(0, 5, 0, 0))
        pjsua_buttons.pack(fill=tk.X)
        
        self.check_pjsua_button = ttk.Button(pjsua_buttons, text="检查", command=self.check_pjsua, width=8)
        self.check_pjsua_button.pack(side=tk.LEFT, padx=5)
        
        self.browse_pjsua_button = ttk.Button(pjsua_buttons, text="浏览", command=self.browse_pjsua, width=8)
        self.browse_pjsua_button.pack(side=tk.LEFT, padx=5)
        
        self.download_pjsua_button = ttk.Button(pjsua_buttons, text="下载", command=self.download_pjsua, width=8)
        self.download_pjsua_button.pack(side=tk.LEFT, padx=5)
        
        self.auto_port_button = ttk.Button(pjsua_buttons, text="自动查找端口", command=self.auto_find_port, width=14)
        self.auto_port_button.pack(side=tk.LEFT, padx=5)
        
        # 为窗口关闭事件绑定处理函数
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # 启动时自动检查PJSUA
        self.root.after(500, self.check_pjsua)
        
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
        
    def browse_pjsua(self):
        """浏览并选择pjsua.exe路径"""
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="选择pjsua.exe文件",
            filetypes=(("可执行文件", "*.exe"), ("所有文件", "*.*"))
        )
        if filename:
            self.pjsua_path_entry.delete(0, tk.END)
            self.pjsua_path_entry.insert(0, filename)
            self.check_pjsua()
    
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
        
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_text.config(state=tk.NORMAL)  # 允许修改
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)  # 滚动到最后
        self.log_text.config(state=tk.DISABLED)  # 恢复只读
        print(f"[{timestamp}] {message}")
    
    def find_available_port(self, start_port=5060):
        """查找可用的SIP端口"""
        port = start_port
        
        # 尝试最多10个端口
        for i in range(10):
            try:
                # 创建测试套接字
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind(('0.0.0.0', port))
                s.close()
                self.log(f"找到可用端口: {port}")
                return port
            except:
                # 端口不可用，尝试下一个
                self.log(f"端口 {port} 不可用，尝试下一个端口")
                port += 2  # SIP端口通常使用偶数
        
        # 如果所有尝试都失败，返回随机端口
        port = random.randint(10000, 60000)
        self.log(f"使用随机端口: {port}")
        return port
        
    def check_pjsua(self):
        pjsua_path = self.pjsua_path_entry.get()
        try:
            # 检查路径是否存在
            if not os.path.exists(pjsua_path):
                self.log(f"PJSUA路径不存在: {pjsua_path}")
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
                self.log(f"PJSUA检测成功: {pjsua_path}")
                return True
            else:
                self.log(f"PJSUA似乎不工作: {result.stderr}")
                messagebox.showerror("PJSUA检测失败", 
                    f"PJSUA找到了，但无法正常运行。\n错误信息: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"PJSUA检测失败: {str(e)}")
            messagebox.showerror("PJSUA检测失败", 
                f"PJSUA检测时出错: {str(e)}\n\n您需要下载并安装PJSUA才能连接到SIP服务器。")
            return False
        
    def login(self):
        server = self.server_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        pjsua_path = self.pjsua_path_entry.get()
        port = self.port_entry.get()
        
        if not server or not username:
            self.log("服务器地址和用户名不能为空")
            return
            
        # 检查端口是否有效
        try:
            port = int(port)
            if port < 1024 or port > 65535:
                self.log("端口号必须在1024-65535之间")
                return
        except ValueError:
            self.log("请输入有效的端口号")
            return
            
        # 检查PJSUA是否可用
        if not os.path.exists(pjsua_path):
            self.log(f"PJSUA路径不存在: {pjsua_path}")
            messagebox.showerror("登录失败", "找不到PJSUA可执行文件，请检查路径或下载安装PJSUA。")
            return
        
        # 如果已经有进程在运行，先结束它    
        if self.process:
            try:
                self.process.terminate()
                self.log("已终止之前的连接")
            except:
                pass
            self.process = None
            
        try:
            self.log(f"尝试连接到服务器: {server}")
            self.log(f"用户名: {username}")
            
            # 更新状态
            self.status_label.config(text="正在连接...", foreground="orange")
            
            # 禁用登录按钮，防止重复操作
            self.login_button.state(['disabled'])
            
            # 构建PJSUA命令
            cmd = [
                pjsua_path,
                f"--id=sip:{username}@{server}",
                f"--registrar=sip:{server}",
                "--realm=*",
                f"--username={username}",
                f"--password={password}",
                "--log-level=4",
                "--app-log-level=4",
                f"--local-port={port}"
            ]
            
            self.log(f"启动PJSUA: {' '.join(cmd)}")
            
            # 启动PJSUA进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True
            )
            
            # 启动线程读取输出
            thread = threading.Thread(target=self.read_output)
            thread.daemon = True
            thread.start()
            
            # 添加状态检查定时器，10秒后检查连接状态
            self.root.after(10000, self.check_login_status)
            
        except Exception as e:
            self.log(f"登录失败: {str(e)}")
            self.status_label.config(text="连接失败", foreground="red")
            self.login_button.state(['!disabled'])
            messagebox.showerror("登录失败", f"连接到服务器时出错: {str(e)}")
    
    def read_output(self):
        """读取PJSUA进程的输出"""
        if not self.process:
            return
            
        # 检测帐户ID正则表达式
        account_pattern = re.compile(r"\*\[\s*(\d+)\]\s+(sip:(\d+)@[^:]+)")
        
        for line in iter(self.process.stdout.readline, ''):
            # 在UI线程中更新日志
            self.root.after(0, lambda msg=line.strip(): self.log(msg))
            
            # 检测注册成功 - 增加更多匹配模式
            if ("registration success" in line and "status=200" in line) or \
               ("registration success" in line and "OK" in line) or \
               ("REGISTER" in line and "200 OK" in line) or \
               ("Registration success" in line):
                self.root.after(0, self.login_completed)
            
            # 检测账号信息
            account_match = account_pattern.search(line)
            if account_match:
                acc_id = account_match.group(1)
                sip_uri = account_match.group(2)
                username = account_match.group(3)
                self.root.after(0, lambda a=acc_id, s=sip_uri, u=username: self.update_account_info(a, s, u))
                
            # 检测来电
            if "Incoming INVITE" in line or "incoming call" in line:
                self.root.after(0, lambda: self.log("检测到来电"))
                
            # 检测通话建立 - 增加多种模式匹配
            if "Call established" in line or "call connected" in line or "Media active" in line:
                self.root.after(0, lambda: self.call_established())
                
            # 检测通话状态更新为确认
            if "state changed to CONFIRMED" in line or "Call state: CONFIRMED" in line:
                self.root.after(0, lambda: self.call_established())
                
            # 检测通话结束 - 增加多种模式匹配
            if "Call disconnected" in line or "call disconnected" in line or "Call state: DISCONNECTED" in line:
                self.root.after(0, lambda: self.call_disconnected())
                
            # 检测拨号相关消息
            if "Making call" in line:
                self.root.after(0, lambda: self.log("正在发起呼叫..."))
            if "Call state" in line:
                self.root.after(0, lambda msg=line: self.log(f"呼叫状态: {msg}"))
            if "Sending INVITE" in line:
                self.root.after(0, lambda: self.log("发送INVITE请求..."))
            if "180 Ringing" in line:
                self.root.after(0, lambda: self.log("对方正在响铃..."))
                self.root.after(0, lambda: self.call_status_label.config(text="对方响铃中...", foreground="orange"))
            if "200 OK" in line and "INVITE" in line:
                self.root.after(0, lambda: self.log("对方已接听..."))
            if "Media will be active soon" in line:
                self.root.after(0, lambda: self.log("媒体即将激活..."))
                
            # 检测挂断相关消息
            if "BYE sent" in line:
                self.root.after(0, lambda: self.log("已发送挂断请求..."))
                
            # 检测错误信息
            if "Unable to make call" in line:
                error_msg = line
                self.root.after(0, lambda msg=error_msg: self.log(f"拨号失败: {msg}"))
                self.root.after(0, lambda: self.status_label.config(text="已连接", foreground="green"))
                self.root.after(0, lambda: self.call_status_label.config(text="拨打失败", foreground="red"))
                self.root.after(0, lambda: self.dial_button.state(['!disabled']))
                
        # 如果进程结束了
        if hasattr(self.process, 'stdout') and self.process.stdout:
            self.process.stdout.close()
        self.root.after(0, lambda: self.log("PJSUA进程已结束"))
        self.root.after(0, lambda: self.status_label.config(text="未连接", foreground="red"))
        self.root.after(0, lambda: self.account_label.config(text="无", foreground="gray"))
        self.root.after(0, lambda: self.call_status_label.config(text="无通话", foreground="gray"))
        self.root.after(0, lambda: self.call_time_label.config(text="00:00:00", foreground="gray"))
        self.root.after(0, lambda: self.login_button.state(['!disabled']))
        self.root.after(0, lambda: self.dial_button.state(['disabled']))
        self.root.after(0, lambda: self.hangup_button.state(['disabled']))
        self.process = None
        
    def update_account_info(self, acc_id, sip_uri, username):
        """更新账号信息显示"""
        self.log(f"当前活跃账号: #{acc_id} {sip_uri}")
        self.account_label.config(text=f"{username}@{sip_uri.split('@')[1]}", foreground="blue")
        
    def login_completed(self):
        # 避免重复调用
        if self.is_connected:
            return
            
        self.is_connected = True
        self.status_label.config(text="已连接", foreground="green")
        self.account_label.config(text="正在获取...", foreground="blue")
        self.call_status_label.config(text="空闲", foreground="green")
        self.dial_button.state(['!disabled'])
        
        # 请求当前账号信息
        try:
            if self.process:
                # 发送d命令获取状态
                self.process.stdin.write("d\r\n")
                self.process.stdin.flush()
                self.log("已请求账号状态信息")
        except Exception as e:
            self.log(f"请求账号信息失败: {str(e)}")
        
    def make_call(self):
        destination = self.dial_entry.get()
        
        if not destination:
            self.log("请输入要拨打的号码")
            return
            
        if not self.is_connected or not self.process:
            self.log("未连接到SIP服务器，无法拨打电话")
            return
            
        try:
            self.log(f"正在拨打: {destination}")
            
            # 更新状态
            self.status_label.config(text="已连接", foreground="green")
            self.call_status_label.config(text="正在拨号...", foreground="orange")
            
            # 禁用拨号按钮，防止重复操作
            self.dial_button.state(['disabled'])
            
            # 向PJSUA发送拨号命令
            server = self.server_entry.get()
            
            # 清空输入缓冲区
            self.process.stdin.write("\r\n")
            self.process.stdin.flush()
            time.sleep(0.1)
            
            # 发送m命令
            self.process.stdin.write("m\r\n")
            self.process.stdin.flush()
            time.sleep(0.1)
            
            # 发送目标URI
            full_url = f"sip:{destination}@{server}"
            self.process.stdin.write(f"{full_url}\r\n")
            self.process.stdin.flush()
            
            # 记录完整的拨号URL
            self.log(f"拨号URL: {full_url}")
            
        except Exception as e:
            self.log(f"拨打电话失败: {str(e)}")
            self.status_label.config(text="已连接", foreground="green")
            self.call_status_label.config(text="拨打失败", foreground="red")
            self.dial_button.state(['!disabled'])
            
    def call_established(self):
        self.call_in_progress = True
        self.status_label.config(text="已连接", foreground="green")
        self.call_status_label.config(text="通话中", foreground="green")
        self.hangup_button.state(['!disabled'])
        
        # 开始计时
        self.call_start_time = time.time()
        self.update_call_timer()
        
    def update_call_timer(self):
        """更新通话时间"""
        if not self.call_in_progress:
            return
            
        elapsed = int(time.time() - self.call_start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.call_time_label.config(text=time_str, foreground="blue")
        
        # 每秒更新一次
        self.call_timer_id = self.root.after(1000, self.update_call_timer)
        
    def call_disconnected(self):
        self.call_in_progress = False
        
        # 停止计时器
        if self.call_timer_id:
            self.root.after_cancel(self.call_timer_id)
            self.call_timer_id = None
        
        # 重置通话时间显示
        self.call_time_label.config(text="00:00:00", foreground="gray")
        
        if self.is_connected:
            self.status_label.config(text="已连接", foreground="green")
            self.call_status_label.config(text="空闲", foreground="green")
            self.dial_button.state(['!disabled'])
        else:
            self.status_label.config(text="未连接", foreground="red")
            self.call_status_label.config(text="无通话", foreground="gray")
        self.hangup_button.state(['disabled'])
        
    def hangup(self):
        if not self.call_in_progress or not self.process:
            self.log("当前没有通话，无法挂断")
            return
            
        try:
            self.log("正在结束通话...")
            
            # 更新状态
            self.call_status_label.config(text="结束通话中...", foreground="orange")
            
            # 禁用挂断按钮，防止重复操作
            self.hangup_button.state(['disabled'])
            
            # 向PJSUA发送挂断命令，使用\r\n确保命令发送
            self.process.stdin.write("h\r\n")
            self.process.stdin.flush()
            
            # 再次发送回车确保命令被执行
            time.sleep(0.1)
            self.process.stdin.write("\r\n")
            self.process.stdin.flush()
            
            # 如果5秒内通话没有断开，强制断开
            self.root.after(5000, self.check_hangup_status)
            
        except Exception as e:
            self.log(f"挂断失败: {str(e)}")
            self.call_status_label.config(text="挂断失败", foreground="red")
            self.hangup_button.state(['!disabled'])
            
    def check_hangup_status(self):
        """检查挂断是否成功，如果仍在通话则强制断开"""
        if self.call_in_progress:
            self.log("挂断超时，强制断开通话")
            self.call_disconnected()
            
    def check_pjsua_status(self):
        """直接检查PJSUA状态"""
        if not self.process:
            return
            
        try:
            # 向PJSUA发送状态查询命令
            self.process.stdin.write("d\n")  # 'd'命令用于显示状态
            self.process.stdin.flush()
            
            # 5秒后再次检查
            self.root.after(5000, self.check_pjsua_status)
        except:
            pass
    
    def on_exit(self):
        """退出程序时清理资源"""
        if self.process:
            try:
                self.process.terminate()
                self.log("已终止PJSUA进程")
            except:
                pass
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

    def auto_find_port(self):
        """自动查找可用端口"""
        port = self.find_available_port(5070)
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, str(port))
        self.log(f"已自动设置端口为: {port}")

    def check_login_status(self):
        """检查连接状态并更新UI"""
        # 如果进程仍在运行，但状态未更新为已连接，则检查是否有注册成功的日志信息
        if self.process and not self.is_connected:
            # 获取日志内容
            log_content = self.log_text.get("1.0", tk.END)
            
            # 检查是否有注册成功的信息
            if ("registration success" in log_content and "status=200" in log_content) or \
               ("registration success" in log_content and "OK" in log_content) or \
               ("REGISTER" in log_content and "200 OK" in log_content) or \
               ("Online status: Online" in log_content):
                self.log("检测到注册已成功，但状态未更新，手动更新状态")
                self.login_completed()
            else:
                # 如果还未连接成功，继续等待5秒后再次检查
                self.root.after(5000, self.check_login_status)

if __name__ == "__main__":
    client = SIPClientTk()
    client.run() 