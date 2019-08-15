from threading import Thread
import time

def func(param):
    for i in range(10):
        print(i)
        time.sleep(1)

class A(Thread):
    def __init__(self,**kwargs):
        Thread.__init__(self)

    def run(self):
        for i in range(10):
            print(i)
            time.sleep(1)


if __name__ == '__main__':

    # 第一种调用线程的方式
    # thread_func = Thread(target=func,args=(1,))
    # thread_func.start()

    # 第二种调用线程的方式
    A().start()
