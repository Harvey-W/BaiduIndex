import urllib.request
import urllib
import time
from bs4 import BeautifulSoup
import socket
import gzip
import threading

class Proxy_pool():
    def __init__(self):
        socket.setdefaulttimeout(3)  #设置全局超时时间
        self.ip_lst=[]
        self.lock=threading.Lock()
        self.threads=[]
        self.doc = open('C:\\Users\\tcsd\\Desktop\\MyDataWork\\tools\\获取百度指数\\proxy.txt','w')  #新建一个储存有效IP的文档    
        
    def get_ip_lst(self):
        for page in range(1,4):
            #proxy = {'http': '45.124.64.142:11319'}
            url = 'http://www.xicidaili.com/wn/'+str(page) #西刺代理
            #url = 'http://lab.crossincode.com/proxy/' #crossin代理池
            #url = 'http://www.kuaidaili.com/free/inha/%s/'%page #快代理
            
            headers={'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
            #proxy_support = urllib.request.ProxyHandler(proxy)
            #opener = urllib.request.build_opener(proxy_support)
            #opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
            #urllib.request.install_opener(opener)
            rep = urllib.request.Request(url=url,headers=headers)
            resp=urllib.request.urlopen(rep)
            
            encoding = resp.info().get('Content-Encoding') #个别页面用了gzip
            if encoding == 'gzip': 
                content=gzip.decompress(resp.read()).decode('utf-8')
            else:
                content = resp.read().decode('utf-8')
            
            
            print('get page',page)
            soup = BeautifulSoup(content,'lxml')
            trs = soup.findAll('tr')
            for x in range(2, len(trs)):
                ip = trs[x]
                tds = ip.findAll('td')
                #if tds == []:
                #    continue
                ip_temp = tds[1].contents[0] + ":" + tds[2].contents[0]
                self.ip_lst.append(ip_temp)
            time.sleep(2)
            #print(self.ip_lst)
        
    def test(self, i):
        url = "http://index.baidu.com/" 
        try:
            proxy_support = urllib.request.ProxyHandler({'http':self.ip_lst[i]})
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64)")]
            urllib.request.install_opener(opener)
            resp = urllib.request.urlopen(url)
            if resp.code == 200:
                self.lock.acquire() #获得锁
                print(self.ip_lst[i],'is OK')        
                self.doc.write('%s\n' %self.ip_lst[i])
                self.lock.release()     #释放锁
        except Exception as e:
            self.lock.acquire()
            print(self.ip_lst[i],e)
            self.lock.release()
    #单线程验证
    '''for i in range(len(self.ip_lst)):
        test(i)'''

    def main(self):
        a.get_ip_lst()
        for i in range(len(self.ip_lst)):    #多线程
            thread=threading.Thread(target=a.test,args=[i])
            self.threads.append(thread)
            thread.start()
        for thread in self.threads:
            thread.join() #阻塞主进程，等待所有子线程结束       
        self.doc.close()

if __name__ == '__main__':
    a = Proxy_pool()
    a.main()
