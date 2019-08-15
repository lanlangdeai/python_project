from multiprocessing import Process,Queue
import time

def func(param,queue):
    while True:
        time.sleep(1)
        param = param + 1
        queue.put(param)





if __name__ == '__main__':
    queue = Queue()
    process_func = Process(target=func,args=(1,queue))
    process_func.start()
    while True:
        print(queue.get())
