import threading
import urllib
from tools import user_agent
import queue
import os
import re
import urllib.request as ur

# 抓取的总微博条数
count = 0
# 避免重复抓取相同URL的博客，set存放URL
catched_set = set()

class CSDN_Spider(threading.Thread):
    # 构造函数
    def __init__(self,queue,blog_name):
        threading.Thread.__init__(self)
        # 初始化 队列
        self.queue = queue
        # 初始化request请求对象
        opener = urllib.request.build_opener(urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        # 设置代理IP
        # proxy_handler = ur.ProxyHandler({'http': self.get_proxy()})
        # opener = ur.build_opener(proxy_handler)
        # 设置http的请求头
        opener.addHeaders = user_agent.get_user_agent_pc()
        # 初始化opener对象
        self.opener = opener
        # 初始化一级列表页面的URL地址
        url = 'https://blog.csdn.net/' + blog_name + '/'
        # request请求一级列表页面
        res = opener.open(url, timeout=500)
        # 保存服务器响应的网页数据
        data = res.read()
        # 初始化博客名称
        self.blog_name= blog_name
        # 通过一级页面的列表数据获得二级页面（博客详情页面）地址
        self.blog_urls= re.compile('/' + blog_name + '/article/details/' + '\d*').findall(data.decode('utf-8'))
        # 初始化线程锁
        self.lock = threading.Lock()

    # 多线程的网页抓取执行函数
    def run(self):
        # 全局变量 抓取博客数量
        global count
        # 全局函数 去重复集合
        global catched_set
        while True:
            # 去重函数
            self.distinct()
            # 从管道中取出一个博客URL来抓取
            url = self.queue.get()
            # 对多个线程的可同时访问的属性，进行上锁
            self.lock.acquire()  # lock
            count += 1
            print('已经抓取：' + str(count)+'正在抓取:'+url)
            # 解锁
            self.lock.release()  # unlock

            try:
                # 抓取博客文章内容
                res = self.opener.open(url, timeout=500)
            except Exception as e:
                print('error code:', e.code)
                count -= 1
                # 相当于删除队列的最新元素，并通知join方法
                self.queue.task_done()
                continue
            else:
                data = res.read()

            # 提取标题作为文件名称
            title = self.find_title(data)
            # 将文章存储在本地
            self.save_data(data,title)

            # 解码，预防乱码
            data =data.decode('utf-8')
            # 在当前页面中，再次查找其他博客URL
            self.blog_urls = re.compile('/'+self.blog_name+'/article/details/'+'\d*').findall(data)
            # 相当于删除队列的最新元素，并通知join方法
            self.queue.task_done()

    # 通过抓到的博客文章内容，截取文章标题
    def find_title(self, data):
        data = data.decode('utf-8')
        begin = data.find(r'<title>')+7
        end = data.find('</title>')
        # 切片截取博客文章的标题
        return data[begin:end]

    # 把抓到的博客，存储到固定路径，并重新命名，名字为通过find_title方法获得的标题
    def save_data(self, data, filename):
        # 判断路径是否存在，不存在新建
        if not os.path.exists('./blog'):
            blog_path = os.path.join(os.path.abspath('.'),'blog')
            os.mkdir(blog_path)
        # 去除'/'字符
        filename =filename.replace('/','-')
        # 把博客内容写入本地文件
        with open('./blog/'+filename+'.html','wb') as f:
            f.write(data)

    # 出去重复的url，防止循环抓取
    def distinct(self):
        for url in self.blog_urls:
            url = 'http://blog.csdn.net' + url
            # 判断该博客内容是否已经抓过，是否在set中存在这个URL
            if url not in catched_set:
                    # 不存在，下次去抓取
                    self.queue.put(url)
                    # 抓取成功后，把URL放入到去重set中，
                    catched_set.add(url)


if __name__ == '__main__':

    '''
        析页面流程-- 定位博客列表URL https://blog.csdn.net/kzl_knight
        分析列表页源代码—筛选每一篇博客的URL地址 https://blog.csdn.net/kzl_knight/article/details/90899356
        分析列表页源代码—总结分页规律 https://blog.csdn.net/kzl_knight/article/list/2?
    '''
    # 获取输入博客名称
    blog_name = 'kzl_knight'
    # blog_name = 'yicoder'

    # 初始化队列queue对象，用于线程之间的通信
    queue = queue.Queue()

    # 初始化多线程并启动，每个线程负责抓取一个博客
    thread_count = 10
    for i in range(thread_count):
        # 初始化线程
        t = CSDN_Spider(queue,blog_name)
        # 设置为守护线程，父线程执行完毕后，子线程也跟着退出
        t.setDaemon(True)
        # 启动线程
        t.start()
    # 相当于等待队列为空，才执行其他操作
    queue.join()

    print('抓取完成--------------end-------------------')
    print('共抓取:'+str(count))