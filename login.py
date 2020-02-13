from selenium import webdriver
import random
import pickle


with open('proxy.txt') as f:
    proxy_lst = f.read().split('\n')
options = webdriver.ChromeOptions()
options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"')
options.add_argument('--proxy-server=%s'%random.choice(proxy_lst))
#options.add_argument('--headless')
#options.add_argument('--disable-gpu')
#options.add_argument('--ssl-protocol=any') 改变协议


browser = webdriver.Chrome(chrome_options=options)
browser.implicitly_wait(30)
browser.get('http://index.baidu.com/')

print(browser.get_cookies())

cookies = pickle.load(open('cookie.pkl','rb'))
for cookie in cookies:
    browser.add_cookie(cookie)

browser.refresh()

print(browser.get_cookies())
