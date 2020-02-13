import urllib.request
import json
import random
from bs4 import BeautifulSoup

proxy = {'http': '118.114.77.47:8080'}
url = 'http://icanhazip.com/'
proxy_support = urllib.request.ProxyHandler(proxy)
opener = urllib.request.build_opener(proxy_support)
opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
urllib.request.install_opener(opener)
resp=urllib.request.urlopen(url, timeout=5)
content=resp.read()
    
    

soup = BeautifulSoup(content,'lxml')
