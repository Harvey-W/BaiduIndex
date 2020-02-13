'''

两种获取图片方法：
1. 直接获取整图（已测试，不精准，可能需要训练库）
2. 分数字获取单个图片再拼接
三种图像识别：
1. SVM
2. TensorFlow
3. 卷积神经网络
4. tesseract+binarizing+灰度图（提高速度）+样本训练(或修正表）
解决：
1. 判断cookies时效(requests) √
2. 多线程（不好用） - 采用分布式
3. 900多个词开始验证码，等待时间（无高质量ip）√
4. 弹出验证码时返回值error √
5. 断线重连 √
6. 优化速度

'''

from PIL import Image
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from threading import Thread
import get_cookie as gc
#import proxy_pool as pp
import queue
import pytesseract
import sys
import urllib.parse
import pickle
import random
#import time
from datetime import datetime


def set_options(proxy):
    global browser
    global options
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"')
    #options.add_argument('--headless') 
    #options.add_argument('--disable-gpu')
    options.add_argument('--proxy-server=%s'%proxy)
    #options.add_argument('--ssl-protocol=any') #改变协议
    
    browser = webdriver.Chrome(chrome_options=options)
    #browser.maximize_window()
    browser.implicitly_wait(5)
    print(proxy)
    browser.get('http://index.baidu.com/')

def get_proxy():
    with open('proxy.txt') as f:
        proxy_lst = f.read().split('\n')
    return (random.choice(proxy_lst))
            

def login():
    cookies = pickle.load(open('cookie.pkl','rb'))
    for cookie in cookies:
        browser.add_cookie(cookie)

def get_img(browser, keyword):
    browser.get('http://index.baidu.com/?tpl=trend&word=%s'
                %urllib.parse.quote(keyword))
    #print('2')
    try: #让无收录的更快显示
        browser.find_element_by_xpath('//div[@class="mw1300 wrapper"]')
    except Exception as e:
        try: #区分无收录还是渲染出错
            target_pc = browser.find_elements_by_class_name('enc2imgVal')[0]
            target_m = browser.find_elements_by_class_name('enc2imgVal')[1]
            #target_pc = WebDriverWait(browser,10,0.5).until(EC.visibility_of(browser.find_element(by=By.CSS_SELECTOR,value='#auto_gsid_5 > div.tabCont.gColor0 > table > tbody > tr:nth-child(2) > td:nth-child(2) > div > span:nth-child(1)'))) 
            #target_m = WebDriverWait(browser,10,0.5).until(EC.visibility_of(browser.find_element(by=By.CSS_SELECTOR,value='#auto_gsid_5 > div.tabCont.gColor0 > table > tbody > tr:nth-child(2) > td:nth-child(2) > div > span:nth-child(2)')))
            #以下无头模式均无法渲染
            #target_pc = WebDriverWait(browser,10,0.5).until(EC.visibility_of(browser.find_element(by=By.XPATH,value='//*[@id="auto_gsid_5"]/div[1]/table/tbody/tr[2]/td[2]/div/span[1]'))) 
            #target_m = WebDriverWait(browser,10,0.5).until(EC.visibility_of(browser.find_element(by=By.XPATH,value='//*[@id="auto_gsid_5"]/div[1]/table/tbody/tr[2]/td[2]/div/span[2]'))) 
        except Exception as e:
            return '0','0'
        loc_pc = target_pc.location  #以下代码能简单表示吗
        size_pc = target_pc.size
        loc_m = target_m.location
        size_m = target_m.size

        pc_region = (int(loc_pc['x']), int(loc_pc['y']),
                     int(loc_pc['x']+size_pc['width']), int(loc_pc['y']+size_pc['height'])
                     )
        m_region = (int(loc_m['x']), int(loc_m['y']),
                     int(loc_m['x']+size_m['width']), int(loc_m['y']+size_m['height'])
                     )
        browser.save_screenshot('index.png')
    else:
        pc_region = m_region = ''
        #print('3')

    #print('4')
    return pc_region, m_region

def img2text(pc_region, m_region):
    try:
        img = Image.open('index.png')
        pc_img = img.crop(pc_region)
        m_img = img.crop(m_region)
        
        (x1, y1) = pc_img.size
        (x2, y2) = m_img.size
        pc_image = pc_img.resize((2*x1, 2*y1), Image.ANTIALIAS)
        m_image = m_img.resize((2*x2, 2*y2), Image.ANTIALIAS)
        pc_code = pytesseract.image_to_string(pc_image)
        m_code = pytesseract.image_to_string(m_image)
    except Exception as e:
        pc_code = m_code = 'error'

    return pc_code, m_code

def patch(pc_index, m_index):
    rep = {'?':'7',
           '.':'', 
           ' ':'',
           'S':'5',
           'H':'17'
           }
    for r in rep:
        pc_index = pc_index.replace(r, rep[r])
        m_index = m_index.replace(r, rep[r])
        
    return pc_index, m_index

def main():
    proxy = get_proxy()
    set_options(proxy)
    login() #oc
    if gc.status_judge(browser): #cookie 时效
        gc.main(browser)
    login() #nc
    
    for keyword in content:
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #测试工期用
    #print('1')
        pc_region, m_region = get_img(browser, keyword.encode('gbk'))
    #print('5')
        if pc_region:
            pc_index, m_index = img2text(pc_region, m_region)
            pc_index, m_index = patch(pc_index, m_index)
            with open('index.txt','a') as f:
                f.write('%s\t%s\t%s\t%s\n'%(keyword,pc_index,m_index,t))
            print('%s\nPC指数是：%s\t移动指数是:%s\n'%(keyword,pc_index,m_index))
        else:
            print('%s\n无收录\n'%keyword)
            with open('index.txt','a') as f:
                f.write('%s\tNaN\tNaN\t%s\n'%(keyword,t))
        with open('keywords_checked.txt','a') as f:
            f.write('%s\n'%keyword)


with open('keywords.txt') as f:
    keywords_lst = [each for each in f.read().split('\n')]
with open('keywords_checked.txt') as f:
    keywords_checked = [each for each in f.read().split('\n')]

content = list(set(keywords_lst)-set(keywords_checked))
content.sort(key=keywords_lst.index)

if __name__ == '__main__':
    main()


''' 多线程
q = queue.Queue()
for keyword in content:
    q.put(keyword)

threads = []
for i in range(3):
    t = Thread(target=main)
    threads.append(t)

for thr in threads:
    thr.start()
'''
'''禁用图片js
prefs={'profile.default_content_setting_values':{
    'images': 2,
    'javascript':2  
    }
       }  
options.add_experimental_option('prefs',prefs)
'''
