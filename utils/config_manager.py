#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器

负责保存和加载用户配置。
"""

import os
import json

class ConfigManager:
    """管理应用程序配置的类"""
    
    def __init__(self, config_file='sip_client_config.json'):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置字典，如果文件不存在则返回默认配置
        """
        default_config = {
            'server': '10.20.25.111',
            'username': '1000',
            'password': '1234',
            'pjsua_path': 'pjsua.exe',
            'port': 5070,
            'auto_login': False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return default_config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return default_config
            
    def save_config(self, config=None):
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典，如果为None则保存当前配置
        """
        if config:
            self.config = config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")
            
    def get(self, key, default=None):
        """
        获取配置项
        
        Args:
            key: 配置项键名
            default: 默认值，如果键不存在则返回此值
            
        Returns:
            配置项的值
        """
        return self.config.get(key, default)
        
    def set(self, key, value):
        """
        设置配置项
        
        Args:
            key: 配置项键名
            value: 配置项的值
        """
        self.config[key] = value
        
    def update(self, new_config):
        """
        更新多个配置项
        
        Args:
            new_config: 包含新配置的字典
        """
        self.config.update(new_config) 