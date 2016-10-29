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


class OutOfCodeTableRangeException(Exception):

    def __init__(self, visit_index, current_index):
        message= 'try to visit {}, but current length is {}'.format(visit_index, current_index-1)
        super(OutOfCodeTableRangeException, self).__init__(message)


class OutOfByteListRangeException(Exception):

    def __init__(self, visit_index, size):
        message= 'try to visit {}, but current size is {}'.format(visit_index, size)
        super(OutOfByteListRangeException, self).__init__(message)


class OCODENotFindAfterInitialException(Exception):

    def __init__(self):
        message = 'OCODE must be find in table after initial'
        super(OCODENotFindAfterInitialException, self).__init__(message)

