#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Author: Yimning
# Date: 2022-11-03 15:00:15
# @Subject  : generate a tail slice from source file

import os

# file_name: 文件路径 
# data_size_times: 数据大小倍数 默认是1024KB=1MB
# offset: 开始的偏移量，也就是代表需要移动偏移的字节数
# whence：可选，默认值为 0。给offset参数一个定义，表示要从哪个位置开始偏移；
#       0代表从文件开头开始算起，
#       1代表从当前位置开始算起，
#       2代表从文件末尾算起。
# usage: tailslice('security',1,"/home/yimning/log/")

def tailslice(file_name, data_size_times,outputPath):
    data_size = data_size_times*1024*1024
    output_file, ext = os.path.splitext(file_name)
    output_file = os.path.join(outputPath,output_file)
    print(output_file)
    with open(file_name, 'rb') as rfile:
        rfile.seek(-data_size, 2)
        with open('{0}{1}'.format(output_file, ext), 'wb') as wfile:
            wfile.write(rfile.read())


if __name__ == '__main__':
    tailslice('security',1,"/home/yimning/yimning/app/python/1/")