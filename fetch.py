#!/usr/bin/python
# -*- coding: utf-8 -*-

# http://www.shangxueba.com/store_2040588_1.html

# http://selenium-python.readthedocs.org/en/latest/installation.html

'''
免费代理 IP地址: http://www.youdaili.cn/
'''

import sys,re,random,time,os
import socket
from socket import error as socket_error
import threading
import urllib2,cookielib
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

proxyFilePath = time.strftime("%Y%m%d")

def testSocket(ip, port):
  '''
  socket连接测试,用来检测proxy ip,port 是否可以正常连接
  '''
  print '正在测试socket连接...'
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.settimeout(10)
    sock.connect((ip, int(port)))
    #sock.send('meta')
    sock.close()
    print ip+':'+port+'--status:ok'
    return 1
  except socket_error as serr: # connection error
    sock.close()
    print ip+':'+port+'--status:error--Connection refused.'
    return 0

def getDriver(httpProxy = '', type='Firefox'):
  if type == 'Firefox':
    proxy = Proxy({
      'proxyType': ProxyType.MANUAL,
      'httpProxy': httpProxy,
      'ftpProxy': httpProxy,
      'sslProxy': httpProxy,
      'noProxy': '' # set this value as desired
      })
    firefox_profile = FirefoxProfile()
    #firefox_profile.add_extension("firefox_extensions/adblock_plus-2.5.1-sm+tb+an+fx.xpi")
    firefox_profile.add_extension("firefox_extensions/webdriver_element_locator-1.rev312-fx.xpi")
    firefox_profile.set_preference("browser.download.folderList",2)
    firefox_profile.set_preference("webdriver.load.strategy", "unstable")
    #driver = webdriver.Firefox(firefox_profile = firefox_profile, proxy=proxy, firefox_binary=FirefoxBinary('/usr/bin/firefox'))
    #driver = webdriver.Firefox(firefox_profile = firefox_profile, proxy=proxy, firefox_binary=FirefoxBinary("/cygdrive/c/Program\ Files\ (x86)/Mozilla\ Firefox/firefox.exe"))
    driver = webdriver.Firefox(firefox_profile = firefox_profile, proxy=proxy)
  elif type == 'PhantomJS':  #  PhantomJS
    service_args = [
    '--proxy='+httpProxy,
    '--proxy-type=http',
    '--load-images=no',
    ]
    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (X11; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'
    driver = webdriver.PhantomJS(executable_path='windows/phantomjs.exe', service_args=service_args)
  else: # Chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % httpProxy)
    driver = webdriver.Chrome(executable_path='windows/chromedriver.exe', chrome_options=chrome_options)
  return driver

# 多线程处理
class MutiThreadingOpenUrl(threading.Thread):
  def __init__(self, url, id, i):
    threading.Thread.__init__(self)
    self.url = url
    self.id  = id
    self.i   = i
  def run(self):
    openUrl(httpProxy, self.url, self.id, self.i)
  
def openUrl(httpProxy, url, id, i):
  '''
  webdriver.Firefox 打开指定URL,并做跳转到输入验证码页面
  '''
  #driver = getDriver(httpProxy, 'Firefox')
  driver = getDriver(httpProxy, 'PhantomJS')
  #driver = getDriver(httpProxy, 'Chrome')
  driver.set_window_size(500,500)
  #driver.headers = {"Referer" : url}
  driver.set_page_load_timeout(30)
  driver.set_script_timeout(5)
  try:
    driver.get("http://www.shangxueba.com/share/p%s.html" % id)
    driver.execute_script('$(".download_btn a").removeAttr("target")')
    driver.find_element_by_xpath("//div[@class='download_btn']/a/img").click()
    print str(i)," : " , driver.title
    driver.execute_script('$("iframe").remove()')
    # get cookie >>>
    #driver.find_element_by_id("imgVerify").click()
    input = driver.get_cookie("CheckCode")['value']
    print "得到验证码值:", input
    #print driver.get_cookies()
    # get cookie <<<
    #input = raw_input("请输入验证码: ")
    #driver.find_element_by_id("txtVerify").clear()
    driver.find_element_by_xpath("//input[@name='txtVerify']").send_keys(input)
    driver.find_element_by_id("Button1").click()
    #print driver.page_source
    print "TA已经在上学吧网站累计赚钱 ", driver.find_element_by_id("Laballsitegetmoney").text
    print "您本次进行下载，上传者获得 ", driver.find_element_by_id("LabGetMoney").text
  except Exception as e:
    print e
  finally:
    driver.close()
    pass

def personalData(httpProxy):
  
  ids = ['7887966','7872487','7811725','7801698','7801697','7801696','7801695','7801694','7801693','7801692',\
         '7801691','7800808','7496236','7496235','7496234','7496233']
  ids = random.sample(ids, 10)
  i = 0
  for id in ids:
    i = i + 1
    href = "http://www.shangxueba.com/share/p%s.html" % id
    openUrl(httpProxy, href, id, i)
    #thread = MutiThreadingOpenUrl(href, id, i)
    #thread.start()

def getProxyInfo():
  # 得到  proxy info
  for fileName in os.listdir(proxyFilePath):
    os.remove(proxyFilePath+"/"+fileName)
    proxyInfo = fileName.split("-")
    ip   = proxyInfo[0]
    port = proxyInfo[1]
    # 获取 proxy info params
    print proxyInfo[0],proxyInfo[1],proxyInfo[2]
    if testSocket(ip, port):
      httpProxy = ":".join([ip, port])
      proxy = urllib2.ProxyHandler({'http': httpProxy})
      opener = urllib2.build_opener(proxy)
      urllib2.install_opener(opener)
      # 调用
      personalData(httpProxy)
  pass

if __name__ == '__main__':
  getProxyInfo()
  sys.exit()
  # 参数检测
  if len(sys.argv) <> 3:
    print "使用说明:"
    print "python %s proxyIP proxyPort" % sys.argv[0]
    print "proxyIP,proxyPort 获取方式: http://www.youdaili.cn/"
    sys.exit()
  
  ip   = sys.argv[1]
  port = sys.argv[2]
  # 获取 proxy info params
  if testSocket(ip, port):
    httpProxy = ":".join([ip, port])
    proxy = urllib2.ProxyHandler({'http': httpProxy})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    personalData(httpProxy)
  else:
    print "please change another proxy!!"
    sys.exit()
  pass



