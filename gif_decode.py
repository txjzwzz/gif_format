# -*- coding=utf-8 -*-
"""
@author wei.zheng
@date 2016.10.19
注意:f.read()即使读完了文件继续f.read()也不会报错,只是会返回'',要注意这样的情况发生
数据编解码的格式:
    f.read()得到的为str,在Python中本质就是bytes
"""
import struct
import binascii
from gif_helpers import read_bits_value_from_byte
from gif_exceptions import BlockSizeException, BlockTerminatorMissException


class GifDecoder(object):

    _SECCESS = 'read gif success'
    _READ_END_SUCCESS = 'read to gif tailer'
    _GRAPHIC_DATA_SUCCESS = 'read graphic data success'
    _BLOCK_SUCCESS = 'read block success'
    _HEADER_ERROR = 'read header error'
    _LOGIC_SCREEN_DESCRIPTION_EOF = 'read logic screen description end of file'
    _GLOBAL_COLOR_TABLE_EOF = 'read global color table end of file'
    _IMAGE_DESCRIPTOR_EOF = 'read image descriptor end of file'
    _LOCAL_COLOR_TABLE_EOF = 'read local color table end of file'
    _IMAGE_DATA_EOF = 'read image data end of file'
    _EXTENSION_Label_EMPTY = 'read extension label is empty string'
    _IDENTIFY_BYTE_EMPTY = 'identify byte is empty'

    def __init__(self):
        self.header = dict()
        self.logical_screen_descriptor = dict()
        self.global_color_table = []
        self.body_data = []  # 依次存储中间的数据

    def read_gif(self, filepath):
        """
        读取gif
        :param filepath: gif文件路径
            读取时候的存在Color Table中间的数值都是数字
        :return: 为gif图True/不是gif图或者文件读取出现错误False, 'Message'
        """
        with open(filepath, 'rb') as f:
            self.read_head(f)
            if self.header['Signature'] != 'GIF':
                return False, self._HEADER_ERROR
            if not self.read_logical_screen_descriptor(f):
                return False, self._LOGIC_SCREEN_DESCRIPTION_EOF
            if not self.read_global_color_table(f):
                return False, self._GLOBAL_COLOR_TABLE_EOF
            #  读取数据
            while self.identify_block(f) is not True:
                continue
        return True, self._SECCESS

    def identify_block(self, f):
        """
        读取块的标识符,并调用相关的块进行处理
        :param f: 文件读取时的迭代器
        :return: 读取是否结束 True:结束, False:未结束
        """
        identify_byte = binascii.hexlify(f.read(1))
        if identify_byte == '2c':
            graphic_data_info, message = self.read_graphic_data(f)
            self.body_data.append(graphic_data_info)
            if message != self._GRAPHIC_DATA_SUCCESS:
                return False, message
        elif identify_byte == '21':
            extension_label = binascii.hexlify(f.read(1))
            if extension_label == 'f9':
                self.body_data.append(self.read_graphic_control_extension(f))
            elif extension_label == 'fe':
                self.body_data.append(self.read_comment_extension(f))
            elif extension_label == '01':
                self.body_data.append(self.read_plain_text_extension(f))
            elif extension_label == 'ff':
                self.body_data.append(self.read_application_extension(f))
            elif extension_label == '':
                return False, self._EXTENSION_Label_EMPTY
            else:
                print "Unknown", extension_label
                print "skip", GifDecoder.skip_unknown_block(f)
        elif identify_byte == '':  # 如果为''代表文件读完了
            return False, self._IDENTIFY_BYTE_EMPTY
        elif identify_byte == '3b':
            return True, self._READ_END_SUCCESS
        else:
            print "Unknown", self.header['Version'], identify_byte
            print "skip", GifDecoder.skip_unknown_block(f)
        return False

    def read_head(self, f):
        """
        读取gif的header
        :param f: 文件读取时的迭代器
        :return:
        """
        self.header = {'Signature': f.read(3), 'Version': f.read(3)}

    def read_logical_screen_descriptor(self, f):
        """
        读取gif的Logical Screen Descriptor
        :param f: 文件读取时的迭代器
        :return: 成功读取 True/False 读取失败
        """
        block_bytes = f.read(7)
        if len(block_bytes) < 7:  # 读取超出文件范围了
            return False
        self.logical_screen_descriptor['logical_screen_width'] = struct.unpack('H', block_bytes[0:2])[0]
        self.logical_screen_descriptor['logical_screen_height'] = struct.unpack('H', block_bytes[2:4])[0]
        packed_fields = block_bytes[4:5]
        self.logical_screen_descriptor['global_color_table_flag'] = read_bits_value_from_byte(
                                                                            packed_fields, 0, 1)
        self.logical_screen_descriptor['color_resolution'] = read_bits_value_from_byte(
                                                                            packed_fields, 1, 3)
        self.logical_screen_descriptor['sort_flag'] = read_bits_value_from_byte(
                                                                            packed_fields, 4, 1)
        self.logical_screen_descriptor['size_of_global_color_table'] = read_bits_value_from_byte(
                                                                            packed_fields, 5, 3)
        self.logical_screen_descriptor['background_color_index'] = struct.unpack('B', block_bytes[5:6])[0]
        self.logical_screen_descriptor['pixel_aspect_ratio'] = struct.unpack('B', block_bytes[6:7])[0]
        return True

    def read_global_color_table(self, f):
        """
        读取图像的Global Color Table,数据流只有一块
        :param f: 文件读取时的迭代器
        :return: True 正确读取/ False 读取出现错误
        """
        # 判断该字段是否存在
        if self.logical_screen_descriptor['global_color_table_flag'] != 1:
            return True
        length = 3 * pow(2, self.logical_screen_descriptor['size_of_global_color_table']+1)
        block_bytes = f.read(length)
        if len(block_bytes) < length:  # 读取超出文件范围了
            return False
        for i in xrange(length):
            self.global_color_table.append(struct.unpack('B', block_bytes[i:i+1])[0])
        return True

    def read_graphic_data(self, f):
        """
        读取图像数据
        :param f: 文件读取时的迭代器,要注意的是,在进入读取图像数据之前f已经读取了
                Image Separator 用来判断是哪个block
        :return: 这张图像所有信息的dict, 读取成功/失败的消息
        """
        res = dict()
        # 读取Image Descriptor
        image_descriptor_dict, message = self.read_image_descriptor(f)
        if message != self._BLOCK_SUCCESS:
            return res, message
        res['image_descriptor'] = image_descriptor_dict
        local_color_table_list, message = self.read_local_color_table(f, res['image_descriptor'])
        if message != self._BLOCK_SUCCESS:
            return res, message
        res['local_color_table'] = local_color_table_list
        table_based_image_data_dict, message = self.read_table_based_image_data(f)
        if message != self._BLOCK_SUCCESS:
            return res, message
        res['table_based_image_data'] = table_based_image_data_dict
        return res, self._GRAPHIC_DATA_SUCCESS

    @staticmethod
    def read_data_sub_block(f):
        """
        递归读取数据子块,直到读取到长度为0的block terminator
        :param f: 文件读取时的迭代器
        :return: str / None: 中间出现eof的情况
        """
        size_info_byte = f.read(1)
        if size_info_byte == '':
            return None
        size_info = struct.unpack('B', size_info_byte)[0]
        if size_info == 0:
            return ''
        res = f.read(size_info)
        if len(res) < size_info:  # EOF
            return None
        res_next = GifDecoder.read_data_sub_block(f)
        return None if res_next is None else res + res_next

    def read_image_descriptor(self, f):
        """
        读取图像的Image Descriptor, 每张图像有且仅有一个Image Descriptor
        :param f: 文件读取时的迭代器,需要注意的是在进入读取图像数据之前f已经读取了
                Image Separator 用来判断是哪个block
        :return: 包含属性的dict, 成功/失败消息
        """
        res = dict()
        block_bytes = f.read(9)
        if len(block_bytes) < 9:
            return res, self._IMAGE_DESCRIPTOR_EOF
        res['image_separator'] = '2c'
        res['image_left_position'] = struct.unpack('H', block_bytes[0:2])[0]
        res['image_top_position'] = struct.unpack('H', block_bytes[2:4])[0]
        res['image_width'] = struct.unpack('H', block_bytes[4:6])[0]
        res['image_height'] = struct.unpack('H', block_bytes[6:8])[0]
        packed_fields = block_bytes[8:9]
        res['local_color_table_flag'] = read_bits_value_from_byte(packed_fields, 0, 1)
        res['interlace_flag'] = read_bits_value_from_byte(packed_fields, 1, 1)
        res['sort_flag'] = read_bits_value_from_byte(packed_fields, 2, 1)
        res['reversed'] = read_bits_value_from_byte(packed_fields, 3, 2)
        res['size_of_local_color_table'] = read_bits_value_from_byte(packed_fields, 5, 3)
        return res, self._BLOCK_SUCCESS

    def read_local_color_table(self, f, image_descriptor_dict):
        """
        读取图像的Local Color Table
        :param f: 文件读取时的迭代器
        :param image_descriptor_dict: 在Local Color Table之前的Image Descriptor的Dict
        :return: 包含颜色bytes的list, 成功/失败的消息
        """
        local_color_datas = []
        if image_descriptor_dict['local_color_table_flag'] != 1:
            return local_color_datas, self._BLOCK_SUCCESS
        size = image_descriptor_dict['size_of_local_color_table']
        length = 3 * pow(2, size+1)
        block_bytes = f.read(length)
        if len(block_bytes) < length:
            return local_color_datas, self._LOCAL_COLOR_TABLE_EOF
        for i in xrange(length):
            local_color_datas.append(struct.unpack('B', block_bytes[i:i+1])[0])
        return local_color_datas, self._BLOCK_SUCCESS

    def read_table_based_image_data(self, f):
        """
        读取图像的Table Based Image Data
        :param f: 文件读取时的迭代器
        :return: 包含table based image data的dict, 成功/失败信息
        """
        res = dict()
        minimum_code_size_byte = f.read(1)
        if minimum_code_size_byte == '':
            return res, self._IMAGE_DATA_EOF
        res['lzw_minimum_code_size'] = struct.unpack('B', minimum_code_size_byte)[0]
        res['image_data'] = GifDecoder.read_data_sub_block(f)
        if res['image_data'] is not None:
            return res, self._BLOCK_SUCCESS
        else:
            return res, self._IMAGE_DATA_EOF

    @staticmethod
    def skip_unknown_block(f):
        """
        持续读取,直到读取到block Terminator, 以此来跳过unknown的block
        :param f: 文件读取时候的迭代器,注意,已经读取了部分作为block开头的标识
        :return: None
        """
        size_info = struct.unpack('B', f.read(1))[0]
        if size_info == 0:
            return 1
        else:
            return GifDecoder.skip_unknown_block(f) + 1

    @staticmethod
    def read_graphic_control_extension(f):
        """
        读取Graphic Control Extension
        :param f: 文件读取时的迭代器,要注意的是,在进入Graphic Control Extension之前f已经读取了
                Extension Introducer 和Graphic Control Label用来判断是哪个block
        :return: 包含graphic control extension信息的dict
        """
        res = dict()
        res['extension_introducer'] = '21'
        res['graphic_control_label'] = 'f9'
        res['block_size'] = struct.unpack('B', f.read(1))[0]
        if res['block_size'] != 4:
            raise BlockSizeException(block_name="graphic control extension", value=res['block_size'],
                                     excepted_value=4)
        packed_fields = f.read(1)
        res['disposal_method'] = read_bits_value_from_byte(packed_fields, 3, 3)
        res['user_input_flag'] = read_bits_value_from_byte(packed_fields, 6, 1)
        res['transparent_color_flag'] = read_bits_value_from_byte(packed_fields, 7, 1)
        res['delay_time'] = struct.unpack('H', f.read(2))[0]
        res['transparent_color_index'] = struct.unpack('B', f.read(1))[0]
        block_terminator = binascii.hexlify(f.read(1))
        if block_terminator != '00':
            raise BlockTerminatorMissException()
        return res

    @staticmethod
    def read_comment_extension(f):
        """
        读取comment extension
        :param f: 文件读取时的迭代器,要注意的是,在进入Comment Extension之前f已经读取了
                Extension Introducer 和Comment Label用来判断是哪个block
        :return: 包含 comment extension信息的dict
        """
        res = dict()
        res['extension_introducer'] = '21'
        res['comment_label'] = 'fe'
        res['comment_data'] = GifDecoder.read_data_sub_block(f)
        return res

    @staticmethod
    def read_plain_text_extension(f):
        """
        读取Plain Text Extension
        :param f: 文件读取时的迭代器,要注意的是,在进入Plain Text Extension之前f已经读取了
                Extension Introducer 和Plain Text Label用来判断是哪个block
        :return: 包含 plain text extension信息的dict
        """
        res = dict()
        res['extension_introducer'] = '21'
        res['plain_text_label'] = '01'
        res['block_size'] = struct.unpack('B', f.read(1))[0]
        if res['block_size'] != 12:
            raise BlockSizeException(block_name='plain text extension', value=res['block_size'],
                                     excepted_value=12)
        res['text_grid_left_position'] = struct.unpack('H', f.read(2))
        res['text_grid_top_position'] = struct.unpack('H', f.read(2))
        res['text_grid_width'] = struct.unpack('H', f.read(2))
        res['text_grid_height'] = struct.unpack('H', f.read(2))
        res['character_cell_width'] = struct.unpack('B', f.read(1))
        res['character_cell_height'] = struct.unpack('B', f.read(1))
        res['text_foreground_color_index'] = struct.unpack('B', f.read(1))
        res['text_background_color_index'] = struct.unpack('B', f.read(1))
        res['plain_text_area'] = GifDecoder.read_data_sub_block(f)
        return res

    @staticmethod
    def read_application_extension(f):
        """
        读取Application Extension
        :param f: 文件读取时的迭代器,要注意的是,在进入Application Extension之前f已经读取了
                Extension Introducer 和Application Extension Label用来判断是哪个block
        :return: 包含Application Extension信息的dict
        """
        res = dict()
        res['extension_introducer'] = '21'
        res['application_extension_label'] = 'ff'
        res['block_size'] = struct.unpack('B', f.read(1))[0]
        if res['block_size'] != 11:
            raise BlockSizeException(block_name='application extension', value=res['block_size'],
                                     excepted_value=11)
        res['application_identifier'] = [f.read(1) for _ in xrange(8)]
        res['application_authentication_code'] = [f.read(1) for _ in xrange(3)]
        res['application_data'] = GifDecoder.read_data_sub_block(f)
        return res

import time
if __name__ == '__main__':
    decoder = GifDecoder()
    gif_file = "data/test3.gif"
    # decoder.read_gif(gif_file)
    # print decoder.header
    # print decoder.logical_screen_descriptor
    decoder.read_and_write('data/rotate.gif', 'data/try_not_rotate.gif')
    # for item_ in decoder.body_data:
    #     if 'local_color_table' in item_ and len(item_['local_color_table'])>0:
    #         current_color_table = item_['local_color_table']
    #     else:
    #         current_color_table = decoder.global_color_table
    #     if 'table_based_image_data' in item_:
    #         width = item_['image_descriptor']['image_width']
    #         height = item_['image_descriptor']['image_height']
    #
    #         im = Image.new('RGB', (width, height))
    #         pixels = im.load()
    #         iter_res = decompress(item_['table_based_image_data']['lzw_minimum_code_size'], ''.join(item_['table_based_image_data']['image_data']))
    #         decompress_res = ''.join([iter_ for iter_ in iter_res])
    #         for i in xrange(im.size[1]):
    #             for j in xrange(im.size[0]):
    #                 # print i, j, i*im.size[0]+j, im.size[0], im.size[1]
    #                 index_ = struct.unpack('B', decompress_res[i*im.size[0]+j])[0]
    #                 # print i, j, index_, len(current_color_table), current_color_table[index_*3], current_color_table[index_*3+1], current_color_table[index_*3+2]
    #                 pixels[j, i] = (current_color_table[index_*3], current_color_table[index_*3+1], current_color_table[index_*3+2])
    #         im.show()
    #         time.sleep(1)
    #
    # with open('output/info.txt', 'wb') as f:
    #     for k, v in decoder.header.iteritems():
    #         f.write("{} : {}\n".format(k, v))
    #     for k, v in decoder.logical_screen_descriptor.iteritems():
    #         f.write("{} : {}\n".format(k, v))
    #     for index_, k in enumerate(decoder.global_color_table):
    #         if index_ % 3 == 0:
    #             f.write("red: {}\n".format(k))
    #         elif index_ % 3 == 1:
    #             f.write("green: {}\n".format(k))
    #         else:
    #             f.write("blue: {}\n".format(k))
    #     for item_ in decoder.body_data:
    #         for k, v in item_.iteritems():
    #             f.write("{} : {}\n".format(k, v))

