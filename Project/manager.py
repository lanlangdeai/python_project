from multiprocessing import Process,Queue
from threading import Thread
import time
import redis
import urllib.request as ur


# 获取代理IP
def get_proxy():
    redis_conn = redis.Redis(decode_responses=True)
    return redis_conn.get('proxy_addr')



def proxy_pool(wait_seconds=2):
    redis_conn = redis.Redis()
    proxy_addr_old = ''
    while True:
        proxy_addr = ur.urlopen('http://api.ip.data5u.com/dynamic/get.html?order=d314e5e5e19b0dfd19762f98308114ba&sep=4').read().decode('utf-8').strip()
        if proxy_addr != proxy_addr_old:
            proxy_addr_old = proxy_addr
            redis_conn.delete('proxy_addr')
            redis_conn.set('proxy_addr',proxy_addr)
        time.sleep(wait_seconds)



if __name__ == '__main__':
    # 初始化进程池
    proxy_pool_process = Process(target=proxy_pool,args=(2,))
    proxy_pool_process.start()





