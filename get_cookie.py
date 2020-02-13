'''
由于图像识别率不高，所以
采用单独运行获取cookie的模块
这样一来，获取图片的功能也不
方便封装来调用了

实际采用个人账号登陆可以避免
验证码，于是此部分可以封装
进主函数

'''

from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import pytesseract
#import re
import time
import pickle

def set_options():
    global browser
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"')
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=options)
    browser.implicitly_wait(3)
    browser.get('http://index.baidu.com/?tpl=trend')

def status_judge(browser):
    print('judge_start')
    print(browser.get_cookies()[-4]['name'])
    if browser.get_cookies()[-4]['name'] != '__cas__id__':
        print('denied')
        return True
    else:
        print('approved')
        return False   

def get_NewCookies(browser):
    print('get_start')
    browser.get('http://index.baidu.com/?tpl=trend')    
    browser.find_element_by_xpath('//*[@id="tab_pas_cas"]/li[2]').click()
    browser.find_element_by_xpath('//*[@id="cas_userName"]').send_keys('*****')
    browser.find_element_by_xpath('//*[@id="cas_password"]').send_keys('*****')

    target_capt = browser.find_element_by_xpath('//*[@id="cas_imgValid"]')
    loc = target_capt.location
    size = target_capt.size
    capt_region = (int(loc['x']), int(loc['y']), int(loc['x'] + size['width']),
                  int(loc['y'] + size['height']))
    browser.save_screenshot('captcha.png')

    screenshot = Image.open('captcha.png')
    capt_img = screenshot.crop(capt_region)
    (x, y) = capt_img.size
    capt_img = capt_img.resize((3*x, 3*y), Image.ANTIALIAS).convert('L')#转为灰度图

    pixdata = capt_img.load() #二值化
    w ,h = capt_img.size
    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < 200:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255

    capt_img.save('captcha.png')

    captcha = pytesseract.image_to_string(capt_img)
    print(captcha)

    browser.find_element_by_xpath('//*[@id="cas_imageCode"]').send_keys(captcha)
    browser.find_element_by_xpath('//*[@id="cas_submit"]').click()
    print('get_finished')

def main(browser):    
    #set_options()    
    while status_judge(browser): #cookie无效                 
        #browser.refresh() #清空输入框 .clear也可以
        print('again')
        get_NewCookies(browser)
    pickle.dump(browser.get_cookies(), open('cookie.pkl', 'wb')) # cookie有失效期，暂时不宜批量爬取
    print('pickled')
     
    print('quit')

if __name__ == '__main__':
    set_options()
    main(browser)
    browser.quit()
