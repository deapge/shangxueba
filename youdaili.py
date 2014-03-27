#/usr/bin/python
# -*- coding:utf8 -*-

'''
采集最新的代理服务器信息,并存储在mongodb数据库中.
http://www.youdaili.cn/Daili/

此文件功能：
  1.用来从代理服务器页面中获取 代理帐号，并测试，将测试通过帐号存储到 文件中
  
流程:
　　1.得到　http://www.youdaili.cn/　今天最新的URL
   2.打开URL地址,并将 proxy ip,port 解析出来
   　3.　将解析出来的  proxy ip,port 存储在文件中
'''

import sys,re,time,os
import urllib
from bs4 import BeautifulSoup
import socket
import threading
from socket import error as socket_error
import datetime

proxyFilePath = time.strftime("%Y%m%d")
proxyDict = []

class FetchProxyServerThread(threading.Thread):
  def __init__(self, ip, port, title):
    threading.Thread.__init__(self)
    self.ip    = ip
    self.port  = port
    self.title = title
  
  def run(self):
    if testSocket(self.ip, self.port) == 1:# 服务器帐号信息正常,存储起来
      posts = {
               'ip'    : self.ip,
               'port'  : self.port,
               'title' : self.title,
               'last_changed': str(datetime.now())
               }
      #　保存数据 到文件,文件命名规则 proxyIP:proxyPort
      filename = "%s/%s-%s-%s" % (proxyFilePath, self.ip, self.port, self.title)
      file(filename, "w")
      print '帐号添加成功!'
      print posts
    pass

def fetchProxyServer(url):
  '''
   抓取 proxy server 信息
  '''
  response = urllib.urlopen(url)
  result = response.read()
  soup = BeautifulSoup(result)
  spandata = soup.find_all("div",class_="cont_font")[0].find("p")
  item_arr = spandata.text.split()
  for item in item_arr:
    temp  = item.replace(":", " ").replace("@", " ").split()
    if len(temp) != 3: continue
    ip    = temp[0]
    port  = temp[1]
    title = temp[2]
    thread = FetchProxyServerThread(ip, port, title)
    thread.start()

def testSocket(ip, port):
  '''
  socket连接测试
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

def getYoudailiUrl():
  '''
  　　通过urllib2 得到　http://www.youdaili.cn/ 今天最新的 url
  　　返回　今天的URL,带分页的URL
  '''
  linksDict = []
  # 得到主页对应的最新的url
  response = urllib.urlopen("http://www.youdaili.cn/Daili/guonei/")
  result = response.read()
  soup = BeautifulSoup(result)
  url = soup.find_all("ul",class_="newslist_line")[0].find("a")['href']
  linksDict.append(url)
  id = re.compile("http\/(.*?)\.html").findall(url)
  # 得到分页URL
  response = urllib.urlopen(url)
  result = response.read()
  soup = BeautifulSoup(result)
  liList = soup.find_all("ul",class_="pagelist")[0].find_all('li')
  liLen = len(liList) - 3
  for i in range(1, liLen):
    url = "http://www.youdaili.cn/Daili/http/%s_%s.html" % (id, str(i+1))
    linksDict.append(url)
  return linksDict
  pass

if __name__ == '__main__':
  if not os.path.exists(proxyFilePath): os.makedirs(proxyFilePath)
  # 删除昨天的文件夹
  removePath = time.strftime("%Y%m%d",time.gmtime(time.time()-24*3600))
  if os.path.exists(removePath): os.remove(removePath)
  linksDict = getYoudailiUrl()
  for url in linksDict:
    fetchProxyServer(url)
  sys.exit()
  
  
  if len(sys.argv) <= 1:
    print ('Usage: python youdaili.py URL')
  else:
    fetchProxyServer(sys.argv[1])