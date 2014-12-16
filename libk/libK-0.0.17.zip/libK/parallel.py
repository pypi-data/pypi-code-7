# coding=utf-8
__author__ = 'Александр'
import multiprocessing

class Parallel:
    result = []

    def __init__(self, parms, processes=None):
        if processes == None:
            processes = len(parms)
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(processes=processes, )
        for data in parms:
            if isinstance(data, dict):
                func = data['f']
                if 'p' in data.keys:
                    if isinstance(data['p'], tuple):
                        args = data['p']
                    else:
                        args = (data['p'],)
                    pool.apply_async(func, args=args, callback=self.log_result)
                else:
                    pool.apply_async(func, callback=self.log_result)
            elif isinstance(data, list):
                func = data[0]
                if len(data) == 2:
                    if isinstance(data[1], tuple):
                        args = data[1]
                    else:
                        args = (data[1],)
                    pool.apply_async(func, args=args, callback=self.log_result)
                elif len(data) == 1:
                    pool.apply_async(func, callback=self.log_result)
        pool.close()
        pool.join()

    def log_result(self, result):
        # This is called whenever foo_pool(i) returns a result.
        # result is modified only by the main process, not the pool workers.
        self.result.append(result)