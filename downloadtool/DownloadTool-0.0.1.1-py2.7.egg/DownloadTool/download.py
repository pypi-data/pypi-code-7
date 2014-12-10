# -*- coding: utf-8 -*-

'''
默认读取md5.txt文件 创建download文件夹，启用多线程下载，我很懒不写命令行
'''

'''
Last modified time: 2014-11-04 16:08:49
Edit time: 2014-11-04 16:10:41
File name: download.py
Edit by caimaoy
'''
import os
import threading

import st_log as log

log = log.init_log('log/download')
log.debug('init download.log')



# 下载命令行 你需要wget 或者也可以换成pytho库自己下载
#command =r'wget -c store.bav.baidu.com/cgi-bin/download_av_sample.cgi?hash=%s'

# 写明md5的文件
file_name = 'md5.txt'

line = 0
finish_num = 0

# 同步锁 可以不使用
mutex = threading.Lock()

base_path = os.path.dirname(os.path.abspath(__file__))
download_dir = 'download'
download_abs_dir = os.path.join(base_path, download_dir)
abs_filename = os.path.join(base_path, file_name)

wget_path = os.path.join(base_path, '../bin/wget.exe')
wget_path = ''.join(['\"', wget_path, '\"'])
wget_argv = '-c'
download_url = 'store.bav.baidu.com/cgi-bin/download_av_sample.cgi?hash=%s'

command = ' '.join([wget_path, wget_argv, download_url])


def _create_dir(download_abs_dir):
    if os.path.exists(download_abs_dir):
        pass
    else:
        try:
            os.mkdir(download_abs_dir)
        except Exception as e:
            log.error(e)
            import sys
            sys.exit(0)


def _total_line(file_name):
    global line
    with open(file_name) as f:
        for i in f:
            line = line + 1


def _readline_and_download(md5):
    cmd = command % md5
    log.debug('cmd is %s...' % cmd)
    os.system(cmd)
    mutex.acquire()
    global finish_num
    finish_num += 1
    log.debug('completed %.2f%%.' % (float(finish_num) / line * 100))
    mutex.release()


def main():
    """默认读取md5.txt文件 创建download文件夹，启用多线程下载，我很懒不写命令行
    参数了

    :returns: None

    """
    _create_dir(download_abs_dir)
    _total_line(file_name)
    from multiprocessing.dummy import Pool as ThreadPool

    # 线程池数目，一般来说和cpu的线程数一样就ok了
    threading_num = 9
    pool = ThreadPool(threading_num)

    os.chdir(download_abs_dir)
    with open(abs_filename) as f:
        pool.map(_readline_and_download, f)

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
