# -*- coding=utf-8 -*-
"""
根据LZW算法进行编解码
In Gif, LZW starts out with a dictionary of 256 characters(in the base of 8 bits) and use those
as the "standard" character set.
@author wei.zheng
@date 2016.10.22
"""


def lzw_decode(initial_code_size, byte_str_list):
    """
    解压lzw压缩的编码
    :param initial_code_size: 初始编码长度
    :param byte_str_list: 从gif图中得到的byte str的list
                          注意这是经过构建8bit字节之后的数据,需要还原为原来的数据
    :return:
    """