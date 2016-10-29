# -*- coding=utf-8 -*-
"""
lzw 算法
"""
import bitarray
from gif_exceptions import OCODENotFindAfterInitialException


class DecompressHelper(object):

    def __init__(self, lzw_minimum_code_size, max_code_size=12):
        self.minimum_code_size = lzw_minimum_code_size
        self.max_code_size = max_code_size
        self.table = None
        self.clear_code = None
        self.end_code = None
        self.next_code = None
        self.clear_code_initial()

    @staticmethod
    def _set_initial_table(code_size):
        return {i: chr(i) for i in xrange(code_size)}

    def clear_code_initial(self):
        code_size = 2**self.minimum_code_size
        self.table = self._set_initial_table(code_size)
        self.clear_code = code_size
        self.end_code = code_size + 1
        self.next_code = code_size + 2

    @property
    def next_code_size(self):
        return min(self.next_code.bit_length(), self.max_code_size)

    def add(self, string_str):
        self.table[self.next_code] = string_str
        self.next_code += 1

import time
def decompress(lzw_minimum_code_size, media_data, max_code_size=12):
    """
    解压缩
    :param lzw_minimum_code_size: 初始code size
    :param media_data: meida数据
    :param max_code_size: 最大的code size
    :return: 解析出来的数据的迭代器
    """
    codes = bitarray.bitarray(endian='little')
    codes.frombytes(media_data)
    dh = DecompressHelper(lzw_minimum_code_size, max_code_size)
    OCODE = None
    current_idnex = 0
    while True:
        # print codes[current_idnex:current_idnex + dh.next_code_size].to01()[::-1]
        code = int(codes[current_idnex:current_idnex + dh.next_code_size].to01()[::-1], 2)
        current_idnex += dh.next_code_size
        if code == dh.clear_code:
            dh.clear_code_initial()
            OCODE = None
        elif code == dh.end_code:
            break
        else:
            if OCODE is None:
                OCODE = code
                if OCODE not in dh.table:
                    raise OCODENotFindAfterInitialException()
                yield dh.table[OCODE]
            else:
                NCODE = code
                if NCODE in dh.table:
                    res_str = dh.table[NCODE]
                else:
                    res_str = dh.table[OCODE]
                    res_str = res_str + res_str[0]
                yield res_str
                char_str = res_str[0]
                dh.add(dh.table[OCODE] + char_str)
                OCODE = NCODE


