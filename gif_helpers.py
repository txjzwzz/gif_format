# -*- coding=utf-8 -*-
"""
辅助函数
@author wei.zheng
@date 2016.10.20
"""
from gif_exceptions import ByteRangeException, OutOfBitLengthValueException, BitNumberOfByteException


def read_bits_value_from_bytes(byte_, start_index, length):
    """
    从byte中读取某几位bit的数值, 注意这个是按照从最小位到最大位的顺序,也就是 76543210这样的顺序
    :param byte_: 待读取的byte
    :param start_index: 开始的索引下标
    :param length: 读取的长度
    :return: 数值
    """
    if start_index + length > 8:
        raise ByteRangeException()
    val_ = 0
    byte = ord(byte_)
    for i in range(start_index, start_index+length):
        val_ = val_ * 2 + ((byte >> (7-i)) & 1)
    return val_


def write_bits_value_to_bytes(value_length_tuple_list):
    """
    写value到byte_中的start_index到length位数
    :param value_length_tuple_list: list of (value, length) tuple
    :return: byte
    """
    total_length = 0
    # check data
    for value, length in value_length_tuple_list:
        if value >= pow(2, length):
            raise OutOfBitLengthValueException(value, length)
        total_length += length
    if total_length != 8:
        raise BitNumberOfByteException(total_length)
    total_value, length_left = 0, 8
    for value, length in value_length_tuple_list:
        length_left -= length
        total_value += (value << length_left)
    return chr(total_value)


