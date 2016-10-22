# -*- coding=utf-8 -*-
"""
@author wei.zheng
@date 2016.10.22
"""


class ByteRangeException(Exception):

    def __init__(self, msg='byte range out of 8 bits'):
        super(ByteRangeException, self).__init__(msg)


class BlockSizeException(Exception):

    def __init__(self, block_name, value, excepted_value):
        """
        :param block_name: 块名称
        :param value: 当前值
        :param excepted_value: 期望获得的值
        """
        message = 'block size in {} is excepted {}, but get {}'.format(block_name, excepted_value, value)
        super(BlockSizeException, self).__init__(message)


class BlockTerminatorMissException(Exception):

    def __init__(self, msg='excepted block terminator not found'):
        super(BlockTerminatorMissException, self).__init__(msg)
