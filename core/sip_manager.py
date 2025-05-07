#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SIP管理器

管理SIP通信和PJSUA进程。
"""

import re
import time
import threading
import subprocess
from tkinter import messagebox

class SIPManager:
    """SIP通信管理器"""
    
    def __init__(self, client, ui_manager, logger, pjsua_utils):
        """初始化SIP管理器"""
        self.client = client
        self.ui_manager = ui_manager
        self.logger = logger
        self.pjsua_utils = pjsua_utils
        
        self.process = None
        self.is_connected = False
        self.call_in_progress = False
        self.call_start_time = None
        self.call_timer_id = None
        
    def check_pjsua(self):
        """检查PJSUA是否可用"""
        pjsua_path = self.ui_manager.get_pjsua_path()
        return self.pjsua_utils.check_pjsua(pjsua_path)
        
    def login(self, server=None, username=None, password=None):
        """登录到SIP服务器"""
        # 如果未提供参数，从UI获取
        if not server or not username or not password:
            info = self.ui_manager.get_server_info()
            server = info['server']
            username = info['username']
            password = info['password']
            
        pjsua_path = self.ui_manager.get_pjsua_path()
        port = self.ui_manager.get_port()
        
        if not server or not username:
            self.logger.log("服务器地址和用户名不能为空")
            return
            
        # 检查端口是否有效
        try:
            port = int(port)
            if port < 1024 or port > 65535:
                self.logger.log("端口号必须在1024-65535之间")
                return
        except ValueError:
            self.logger.log("请输入有效的端口号")
            return
            
        # 检查PJSUA是否可用
        if not self.check_pjsua():
            return
        
        # 如果已经有进程在运行，先结束它    
        self.cleanup()
            
        try:
            self.logger.log(f"尝试连接到服务器: {server}")
            self.logger.log(f"用户名: {username}")
            
            # 更新状态
            self.ui_manager.update_status("正在连接...", "orange")
            
            # 禁用登录按钮，防止重复操作
            self.ui_manager.disable_login_button()
            
            # 构建PJSUA命令 - 使用最基本的命令
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
            
            self.logger.log(f"启动PJSUA: {' '.join(cmd)}")
            
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
            self.client.root.after(10000, self.check_login_status)
            
            # 5秒后开始检查PJSUA状态
            self.client.root.after(5000, self.check_pjsua_status)
            
        except Exception as e:
            self.logger.log(f"登录失败: {str(e)}")
            self.ui_manager.update_status("连接失败", "red")
            self.ui_manager.enable_login_button()
            messagebox.showerror("登录失败", f"连接到服务器时出错: {str(e)}")
            
    def read_output(self):
        """读取PJSUA进程的输出"""
        if not self.process:
            return
            
        # 检测帐户ID正则表达式 - 增强匹配模式
        account_pattern = re.compile(r"\*\[\s*(\d+)\]\s+(sip:([^@]+)@([^:]+))")
        # 检测更多账户信息格式
        alt_account_pattern = re.compile(r"Account\s+\d+:\s+sip:([^@]+)@([^:]+)")
        
        for line in iter(self.process.stdout.readline, ''):
            # 在UI线程中更新日志
            self.client.root.after(0, lambda msg=line.strip(): self.logger.log(msg))
            
            # 检测注册成功 - 增加更多匹配模式
            if ("registration success" in line and "status=200" in line) or \
               ("registration success" in line and "OK" in line) or \
               ("REGISTER" in line and "200 OK" in line) or \
               ("Registration success" in line):
                self.client.root.after(0, self.login_completed)
            
            # 检测账号信息 - 主要模式
            account_match = account_pattern.search(line)
            if account_match:
                acc_id = account_match.group(1)
                sip_uri = account_match.group(2)
                username = account_match.group(3)
                server = account_match.group(4)
                self.client.root.after(0, lambda a=acc_id, s=sip_uri, u=username, sv=server: 
                                      self.update_account_info(a, s, u, sv))
            
            # 检测账号信息 - 备选模式
            alt_match = alt_account_pattern.search(line)
            if alt_match and not account_match:
                username = alt_match.group(1)
                server = alt_match.group(2)
                self.client.root.after(0, lambda u=username, sv=server:
                                      self.fallback_account_info(u, sv))
                
            # 如果看到账号状态信息但未匹配到正则，尝试提取用户名和服务器
            if "Account" in line and "sip:" in line and not account_match and not alt_match:
                self.client.root.after(0, lambda l=line: self.try_extract_account(l))
                
            # 检测来电
            if "Incoming INVITE" in line or "incoming call" in line:
                self.client.root.after(0, lambda: self.logger.log("检测到来电"))
                
            # 检测通话建立 - 增加多种模式匹配
            if "Call established" in line or "call connected" in line or "Media active" in line:
                self.client.root.after(0, lambda: self.call_established())
                
            # 检测通话状态更新为确认
            if "state changed to CONFIRMED" in line or "Call state: CONFIRMED" in line:
                self.client.root.after(0, lambda: self.call_established())
                
            # 检测通话结束 - 增加多种模式匹配
            if "Call disconnected" in line or "call disconnected" in line or "Call state: DISCONNECTED" in line:
                self.client.root.after(0, lambda: self.call_disconnected())
                
            # 检测拨号相关消息
            if "Making call" in line:
                self.client.root.after(0, lambda: self.logger.log("正在发起呼叫..."))
            if "Call state" in line:
                self.client.root.after(0, lambda msg=line: self.logger.log(f"呼叫状态: {msg}"))
            if "Sending INVITE" in line:
                self.client.root.after(0, lambda: self.logger.log("发送INVITE请求..."))
            if "180 Ringing" in line:
                self.client.root.after(0, lambda: self.logger.log("对方正在响铃..."))
                self.client.root.after(0, lambda: self.ui_manager.update_call_status("对方响铃中...", "orange"))
            if "200 OK" in line and "INVITE" in line:
                self.client.root.after(0, lambda: self.logger.log("对方已接听..."))
            if "Media will be active soon" in line:
                self.client.root.after(0, lambda: self.logger.log("媒体即将激活..."))
                
            # 检测挂断相关消息
            if "BYE sent" in line:
                self.client.root.after(0, lambda: self.logger.log("已发送挂断请求..."))
                
            # 检测错误信息
            if "Unable to make call" in line:
                error_msg = line
                self.client.root.after(0, lambda msg=error_msg: self.logger.log(f"拨号失败: {msg}"))
                self.client.root.after(0, lambda: self.ui_manager.update_status("已连接", "green"))
                self.client.root.after(0, lambda: self.ui_manager.update_call_status("拨打失败", "red"))
                self.client.root.after(0, lambda: self.ui_manager.enable_dial_button())
                
        # 如果进程结束了
        if hasattr(self.process, 'stdout') and self.process.stdout:
            self.process.stdout.close()
        self.client.root.after(0, lambda: self.logger.log("PJSUA进程已结束"))
        self.client.root.after(0, lambda: self.ui_manager.update_status("未连接", "red"))
        self.client.root.after(0, lambda: self.ui_manager.update_account_info("无", "gray"))
        self.client.root.after(0, lambda: self.ui_manager.update_call_status("无通话", "gray"))
        self.client.root.after(0, lambda: self.ui_manager.update_call_time("00:00:00", "gray"))
        self.client.root.after(0, lambda: self.ui_manager.reset_login_button())
        self.client.root.after(0, lambda: self.ui_manager.disable_dial_button())
        self.client.root.after(0, lambda: self.ui_manager.disable_hangup_button())
        self.process = None
        
    def try_extract_account(self, line):
        """尝试从各种格式的行中提取账号信息"""
        try:
            if "sip:" in line:
                # 尝试提取形如 "sip:username@server" 的部分
                start = line.find("sip:")
                if start >= 0:
                    sip_part = line[start:]
                    end = sip_part.find(" ")
                    if end > 0:
                        sip_part = sip_part[:end]
                    
                    # 清理结尾可能的标点
                    sip_part = sip_part.rstrip(",.;:")
                    
                    # 提取用户名和服务器
                    if "@" in sip_part:
                        username = sip_part.split(":")[1].split("@")[0]
                        server = sip_part.split("@")[1]
                        self.fallback_account_info(username, server)
                        return True
            return False
        except Exception as e:
            self.logger.log(f"提取账号信息失败: {str(e)}")
            return False
        
    def update_account_info(self, acc_id, sip_uri, username, server=None):
        """更新账号信息显示"""
        self.logger.log(f"当前活跃账号: #{acc_id} {sip_uri}")
        
        # 如果未提供服务器，尝试从sip_uri中提取
        if not server and "@" in sip_uri:
            server = sip_uri.split('@')[1]
            
        # 更新UI显示
        self.ui_manager.update_account_info(f"{username}@{server}", "blue")
        
        # 保存账号信息到配置
        self.client.config_manager.set('current_username', username)
        self.client.config_manager.set('current_server', server)
    
    def fallback_account_info(self, username, server):
        """备用方法更新账号信息"""
        self.logger.log(f"使用备用方法更新账号信息: {username}@{server}")
        self.ui_manager.update_account_info(f"{username}@{server}", "blue")
        
        # 保存账号信息到配置
        self.client.config_manager.set('current_username', username)
        self.client.config_manager.set('current_server', server)
        
    def login_completed(self):
        """登录成功后的处理"""
        # 避免重复调用
        if self.is_connected:
            return
            
        self.logger.log("登录成功")
        
        # 更新状态
        self.is_connected = True
        self.ui_manager.update_status("已连接", "green")
        
        # 获取登录信息直接显示，避免等待
        info = self.ui_manager.get_server_info()
        if info['username'] and info['server']:
            self.ui_manager.update_account_info(f"{info['username']}@{info['server']}", "blue")
        else:
            self.ui_manager.update_account_info("正在获取...", "blue")
            
        self.ui_manager.update_call_status("空闲", "green")
        
        # 启用拨号按钮
        self.ui_manager.enable_dial_button()
        
        # 更新登录按钮状态
        self.ui_manager.set_login_button_connected()
        
        # 启用断开连接按钮
        self.ui_manager.enable_disconnect_button()
        
        # 立即请求账号信息
        self.request_account_info()
        
        # 设置定期请求账号信息的定时器
        self.setup_account_info_timer()
        
        # messagebox.showinfo("连接成功", "已成功连接到SIP服务器！")
        
    def request_account_info(self):
        """请求当前账号信息"""
        try:
            if self.process and self.process.stdin:
                self.process.stdin.write("d\r\n")
                self.process.stdin.flush()
                self.logger.log("已请求账号状态信息")
        except Exception as e:
            self.logger.log(f"请求账号信息失败: {str(e)}")
            
    def setup_account_info_timer(self):
        """设置定期请求账号信息的定时器"""
        # 定义定时器变量
        self.account_info_timer = None
        
        # 每10秒请求一次账号信息
        def request_regularly():
            if self.is_connected and self.process:
                self.request_account_info()
                # 继续下一次定时
                self.account_info_timer = self.client.root.after(10000, request_regularly)
        
        # 启动第一次定时
        self.account_info_timer = self.client.root.after(10000, request_regularly)
        
    def make_call(self):
        """拨打电话"""
        destination = self.ui_manager.get_dial_number()
        server = self.ui_manager.get_server_info()['server']
        
        if not destination:
            self.logger.log("请输入要拨打的号码")
            return
            
        if not self.is_connected or not self.process:
            self.logger.log("未连接到SIP服务器，无法拨打电话")
            return
            
        try:
            self.logger.log(f"正在拨打: {destination}")
            
            # 更新状态
            self.ui_manager.update_status("已连接", "green")
            self.ui_manager.update_call_status("正在拨号...", "orange")
            
            # 禁用拨号按钮，防止重复操作
            self.ui_manager.disable_dial_button()
            
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
            self.logger.log(f"拨号URL: {full_url}")
            
        except Exception as e:
            self.logger.log(f"拨打电话失败: {str(e)}")
            self.ui_manager.update_status("已连接", "green")
            self.ui_manager.update_call_status("拨打失败", "red")
            self.ui_manager.enable_dial_button()
            
    def call_established(self):
        """通话建立后的处理"""
        self.call_in_progress = True
        self.ui_manager.update_status("已连接", "green")
        self.ui_manager.update_call_status("通话中", "green")
        self.ui_manager.enable_hangup_button()
        
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
        self.ui_manager.update_call_time(time_str, "blue")
        
        # 每秒更新一次
        self.call_timer_id = self.client.root.after(1000, self.update_call_timer)
        
    def call_disconnected(self):
        """通话断开后的处理"""
        self.call_in_progress = False
        
        # 停止计时器
        if self.call_timer_id:
            self.client.root.after_cancel(self.call_timer_id)
            self.call_timer_id = None
        
        # 重置通话时间显示
        self.ui_manager.update_call_time("00:00:00", "gray")
        
        if self.is_connected:
            self.ui_manager.update_status("已连接", "green")
            self.ui_manager.update_call_status("空闲", "green")
            self.ui_manager.enable_dial_button()
        else:
            self.ui_manager.update_status("未连接", "red")
            self.ui_manager.update_call_status("无通话", "gray")
        self.ui_manager.disable_hangup_button()
            
    def hangup(self):
        """挂断电话"""
        if not self.call_in_progress or not self.process:
            self.logger.log("当前没有通话，无法挂断")
            return
            
        try:
            self.logger.log("正在结束通话...")
            
            # 更新状态
            self.ui_manager.update_call_status("结束通话中...", "orange")
            
            # 禁用挂断按钮，防止重复操作
            self.ui_manager.disable_hangup_button()
            
            # 向PJSUA发送挂断命令，使用\r\n确保命令发送
            self.process.stdin.write("h\r\n")
            self.process.stdin.flush()
            
            # 再次发送回车确保命令被执行
            time.sleep(0.1)
            self.process.stdin.write("\r\n")
            self.process.stdin.flush()
            
            # 如果5秒内通话没有断开，强制断开
            self.client.root.after(5000, self.check_hangup_status)
            
        except Exception as e:
            self.logger.log(f"挂断失败: {str(e)}")
            self.ui_manager.update_call_status("挂断失败", "red")
            self.ui_manager.enable_hangup_button()
            
    def check_hangup_status(self):
        """检查挂断是否成功，如果仍在通话则强制断开"""
        if self.call_in_progress:
            self.logger.log("挂断超时，强制断开通话")
            self.call_disconnected()
            
    def check_pjsua_status(self):
        """直接检查PJSUA状态"""
        if not self.process:
            return
            
        try:
            # 向PJSUA发送状态查询命令
            self.process.stdin.write("d\r\n")  # 'd'命令用于显示状态
            self.process.stdin.flush()
            
            # 5秒后再次检查
            self.client.root.after(5000, self.check_pjsua_status)
        except:
            pass
            
    def check_login_status(self):
        """检查连接状态并更新UI"""
        # 如果进程仍在运行，但状态未更新为已连接，则检查是否有注册成功的日志信息
        if self.process and not self.is_connected:
            # 获取日志内容 - 这里应该改为从Logger获取，但为了简化，直接检查UI中的日志文本
            log_content = self.ui_manager.log_text.get("1.0", "end")
            
            # 检查是否有注册成功的信息
            if ("registration success" in log_content and "status=200" in log_content) or \
               ("registration success" in log_content and "OK" in log_content) or \
               ("REGISTER" in log_content and "200 OK" in log_content) or \
               ("Online status: Online" in log_content):
                self.logger.log("检测到注册已成功，但状态未更新，手动更新状态")
                self.login_completed()
            else:
                # 如果还未连接成功，继续等待5秒后再次检查
                self.client.root.after(5000, self.check_login_status)
                
    def cleanup(self):
        """清理资源"""
        if self.process:
            try:
                self.process.terminate()
                self.logger.log("已终止PJSUA进程")
            except:
                pass
            self.process = None

    def unregister(self):
        """从SIP服务器注销但不退出程序"""
        if not self.process:
            self.logger.log("当前未连接到SIP服务器")
            return
            
        try:
            self.logger.log("正在从SIP服务器注销...")
            
            # 如果有通话，先挂断
            if self.call_in_progress:
                self.hangup()
                
            # 向PJSUA发送注销命令 - 先尝试使用PJSUA的ru命令
            if self.process and self.process.stdin:
                self.process.stdin.write("ru\n")
                self.process.stdin.flush()
                self.logger.log("已发送注销命令")
                
                # 给一点时间让PJSUA处理注销
                time.sleep(1)
                
            # 清理资源但不退出程序
            self.cleanup_without_exit()
            
            # 更新状态
            self.is_connected = False
            self.ui_manager.update_status("已断开", "red")
            self.ui_manager.update_account_info("无", "gray")
            self.ui_manager.update_call_status("无通话", "gray")
            
            # 重置按钮状态
            self.ui_manager.reset_login_button()
            self.ui_manager.disable_disconnect_button()
            self.ui_manager.disable_dial_button()
            
        except Exception as e:
            self.logger.log(f"注销过程中出错: {str(e)}")
            
    def cleanup_without_exit(self):
        """清理资源但不退出程序"""
        if self.process:
            try:
                # 终止PJSUA进程
                if self.process.poll() is None:  # 如果进程仍在运行
                    # 尝试通过q命令优雅退出
                    if self.process.stdin:
                        self.process.stdin.write("q\n")
                        self.process.stdin.flush()
                        
                    # 等待一段时间让进程自行终止
                    time.sleep(0.5)
                    
                    # 如果进程仍在运行，强制终止
                    if self.process.poll() is None:
                        self.process.terminate()
                        self.process.wait(timeout=2)
                        
            except Exception as e:
                self.logger.log(f"清理PJSUA进程时出错: {str(e)}")
            finally:
                self.process = None
                
        # 停止所有定时器
        if hasattr(self, 'account_info_timer') and self.account_info_timer:
            self.client.root.after_cancel(self.account_info_timer)
            self.account_info_timer = None
            
        if self.call_timer_id:
            self.client.root.after_cancel(self.call_timer_id)
            self.call_timer_id = None
            
        # 重置状态
        self.call_in_progress = False
        self.call_start_time = None
        
        # 重置登录按钮状态
        self.ui_manager.reset_login_button() 