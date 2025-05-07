#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SIP客户端主程序

这是一个基于PJSUA的SIP客户端，提供图形界面进行SIP电话操作。
"""

from sip_client import SIPClient

if __name__ == "__main__":
    client = SIPClient()
    client.run() 