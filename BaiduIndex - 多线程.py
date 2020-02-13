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
1. 判断cookies时效(requests)
2. 多线程
3. 900多个词开始验证码，等待时间
4. 有未知bug 暂时返回值error
5. 断线重连

'''

from PIL import Image
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from threading import Thread
#from multiprocessing 
import queue
import pytesseract
import sys
import urllib.parse
import pickle
import time



global browser
options = webdriver.ChromeOptions()
options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"')
options.add_argument('--headless') #无头模式不渲染指数所在区域
options.add_argument('--disable-gpu')
#options.add_argument('--ssl-protocol=any') #改变协议
browser = webdriver.Chrome(chrome_options=options)

#browser.maximize_window()
browser.implicitly_wait(2)


def get_NewCookie():
    pass

def login():
    browser.get('http://index.baidu.com/')    
    cookies = pickle.load(open('cookie.pkl','rb'))
    for cookie in cookies:
        browser.add_cookie(cookie)


def get_img(keyword):
    #url = 'http://index.baidu.com/?tpl=trend&word=%s' % urllib.parse.quote(keyword)
    #js ='window.open("%s");' % url
    #browser.execute_script(js)
    #handles = browser.window_handles
    #browser.switch_to.window(handles[len(handles)-1])
    browser = webdriver.Chrome(chrome_options=options)
    login()
    browser.get('http://index.baidu.com/?tpl=trend&word=%s'%urllib.parse.quote(keyword))


    #print('2')
    try: #让无收录的更快显示
        browser.find_element_by_xpath('//div[@class="mw1300 wrapper"]')
    except Exception as e:
        try: #区分无收录还是渲染出错
            target_pc = browser.find_elements_by_class_name('enc2imgVal')[0]
            target_m = browser.find_elements_by_class_name('enc2imgVal')[1]
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
        
    #browser.switch_to.window(handles[0])
    browser.close()
    #print('4')
    #browser.quit()    
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
    while not q.empty():
        try:
            keyword = q.get()
            #print('1')
            pc_region, m_region = get_img(keyword.encode('gbk'))
            #print('5')
            if pc_region:
                pc_index, m_index = img2text(pc_region, m_region)
                pc_index, m_index = patch(pc_index, m_index)
                with open('index.txt','a') as f:
                    f.write('%s\t%s\t%s\n'%(keyword,pc_index,m_index))
                print('%s\nPC指数是：%s\t移动指数是:%s\n'%(keyword,pc_index,m_index))
            else:
                print('%s\n无收录\n'%keyword)
                with open('index.txt','a') as f:
                    f.write('%s\tNaN\tNaN\t%s\n'%(keyword,time.time()))
            with open('keywords_checked.txt','a') as f:
                f.write(keyword+'\n')
        except Exception as e:
            raise e
            continue          

with open('keywords.txt') as f:
    keywords_lst = [each for each in f.read().split('\n')]
with open('keywords_checked.txt') as f:
    keywords_checked = [each for each in f.read().split('\n')]

content = list(set(keywords_lst)-set(keywords_checked))
content.sort(key=keywords_lst.index)

q = queue.Queue()
for keyword in content:
    q.put(keyword)

threads = []
for i in range(11):
    t = Thread(target=main)
    threads.append(t)

for thr in threads:
    thr.start()
