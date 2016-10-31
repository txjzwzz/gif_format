# -*- coding=utf-8 -*-
"""
读取并写Gif到文件中,可以去除不符合规范的bolck,或者添加/删除某些块
每个部位都进行详细地读写分析,主要为了熟悉协议
"""
import struct
import binascii
from gif_helpers import read_bits_value_from_bytes


class GifReWrite(object):

    @classmethod
    def read_and_validate_write(cls, in_filepath, out_filepath):
        """
        读取gif,并将合法的块写入
        :param in_filepath: 输入路径
        :param out_filepath: 输出路径
        :return: None
        """
        with open(in_filepath, 'rb') as f, open(out_filepath, 'wb') as fw:
            cls.read_and_write_header(f, fw)
            pass

    @staticmethod
    def read_and_write_header(f, fw):
        """
        读写文件头
        :param f: 文件读取的迭代器
        :param fw: 文件写入的迭代器
        :return: None
        """
        signature = f.read(3)
        version = f.write(3)
        fw.write(signature)
        fw.write(version)



