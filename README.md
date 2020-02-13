# 获取百度指数(http://index.baidu.com/) 
**批量采集/OCR识别防爬内容/自动填写验证码/cookie过期自检/自动获取代理/断线重连**
- BaiduIndex
  - 单线程：指数图像识别方式是tesseract+binarizing+灰度图，待改进（SVM、TensorFlow、卷积神经网络）
  - 多线程：selenium下无法实现多线程，句柄切换不便。多进程又太消耗内存，因此暂时只有框架
- get_cookie
    考虑到未来的可扩展性，单独拿出来了此模块
- proxy_pool
    参照多种范本改进，加入更多IP获取地址/实现封装
