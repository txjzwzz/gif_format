# -*- coding=utf-8 -*-
"""
根据LZW算法进行编解码
In Gif, LZW starts out with a dictionary of 256 characters(in the base of 8 bits) and use those
as the "standard" character set.
@author wei.zheng
@date 2016.10.22
"""
from gif_exceptions import OutOfCodeTableRangeException, OutOfByteListRangeException
import time


def lzw_decode(initial_code_size, byte_str_list):
    """
    解压lzw压缩的编码
    压缩之后的编码转为8but的时候是这样的
    aaaaaaaa bbbbbbba ccccccbb dddddccc ...
    :param initial_code_size: 初始编码长度
    :param byte_str_list: 从gif图中得到的byte str的list
                          注意这是经过构建8bit字节之后的数据,需要还原为原来的数据
    :return:
    """
    binary_list = ["{0:08b}".format(ord(byte_)) for byte_ in byte_str_list]
    default_table = dict()
    default_table_size = pow(2, initial_code_size)
    clear_code = pow(2, initial_code_size)
    for i in xrange(default_table_size):
        default_table[i] = ("{0:0" + str(initial_code_size) + "b}").format(i)
    current_code_table = dict()  # 当前编码表格
    current_code_size = initial_code_size + 1
    current_byte_index = 0
    current_cut_index = 8  # 当前byte切出来的点,设定为1-8 为0的时候应该去下一个byte
    current_table_index = clear_code + 2  # 编码从codesize+2开始
    res_list = []
    front_code = None  # 上一个提取出来的字符的编码
    while True:
        # print res_list
        # current byte size最大为12,所以最多不过三个byte
        # print current_code_table
        size_left = current_code_size
        code_str = ""
        while True:
            if current_byte_index >= len(binary_list):
                # print res_list
                raise OutOfByteListRangeException(current_byte_index, len(binary_list))
            if size_left <= current_cut_index:
                code_str = binary_list[current_byte_index][current_cut_index-size_left:current_cut_index] + code_str
                current_cut_index -= size_left
                if current_cut_index == 0:
                    # 进位
                    current_cut_index = 8
                    current_byte_index += 1
                break
            else:
                code_str = binary_list[current_byte_index][:current_cut_index] + code_str
                size_left -= current_cut_index
                # 进位
                current_cut_index = 8
                current_byte_index += 1
        print code_str, current_code_size, len(current_code_table)
        # time.sleep(0.3)

        index_ = int(code_str, 2)
        if index_ == clear_code:  # reset status
            current_code_table = dict()
            clear_code = pow(2, initial_code_size)
            current_code_size = initial_code_size + 1
            current_table_index = clear_code + 2
            front_code = ("{0:0" + str(initial_code_size) + "b}").format(0)
        elif index_ == clear_code + 1:  # end of information code
            break
        else:  # from code table
            if index_ >= current_table_index:  # 超出编码的范围
                raise OutOfCodeTableRangeException(index_, current_table_index)
            if index_ < default_table_size:
                res_list.append(default_table[index_])
            else:
                res_list.append(current_code_table[index_])
            # update current code table
            if front_code:  # 当前存在front code
                new_word = "{}{}".format(front_code, res_list[-1][0:initial_code_size])  # 只取当前解析的词的第一个
                current_code_table[current_table_index] = new_word
                front_code = res_list[-1]  # update front code
                current_table_index += 1
                # 处理当前的table长度满了的情况
                if current_table_index == pow(2, current_code_size+1):
                    current_code_size += 1
                    clear_code = pow(2, current_code_size)
                    current_table_index = clear_code + 2
            else:  # 不存在当前的font code
                front_code = res_list[-1]

