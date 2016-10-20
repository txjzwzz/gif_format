# -*- coding=utf-8 -*-
"""
@author wei.zheng
@date 2016.10.19
"""
import struct
from gif_helpers import read_bits_value_from_bytes


class GifDecoder(object):

    def __init__(self):
        self.header = dict()
        self.logical_screen_descriptor = dict()
        self.global_color_table = []

    def read_gif(self, filepath):
        """
        读取gif
        :param filepath: gif文件路径
        :return:
        """
        with open(filepath, 'rb') as f:
            self.read_head(f)
            print self.header
            self.read_logical_screen_descriptor(f)
            print self.logical_screen_descriptor
            self.read_global_color_table(f)
            print self.global_color_table

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
        :return:
        """
        self.logical_screen_descriptor['logical_screen_width'] = struct.unpack('H', f.read(2))[0]
        self.logical_screen_descriptor['logical_screen_height'] = struct.unpack('H', f.read(2))[0]
        packed_fields = f.read(1)
        self.logical_screen_descriptor['global_color_table_flag'] = read_bits_value_from_bytes(
                                                                            packed_fields, 1, 1)
        self.logical_screen_descriptor['color_resolution'] = read_bits_value_from_bytes(
                                                                            packed_fields, 2, 3)
        self.logical_screen_descriptor['sort_flag'] = read_bits_value_from_bytes(
                                                                            packed_fields, 5, 1)
        self.logical_screen_descriptor['size_of_global_color_table'] = read_bits_value_from_bytes(
                                                                            packed_fields, 6, 3)
        self.logical_screen_descriptor['background_color_index'] = struct.unpack('B', f.read(1))[0]
        self.logical_screen_descriptor['pixel_aspect_ratio'] = struct.unpack('B', f.read(1))[0]

    def read_global_color_table(self, f):
        """
        读取图像的Global Color Table,数据流只有一块
        :param f: 文件读取时的迭代器
        :return:
        """
        # 判断该字段是否存在
        if self.logical_screen_descriptor['global_color_table_flag'] != 1:
            return
        length = 3 * pow(2, self.logical_screen_descriptor['size_of_global_color_table']+1)
        for i in range(length):
            self.global_color_table.append(struct.unpack('B', f.read(1))[0])

    @staticmethod
    def read_image_descriptor(f):
        """
        读取图像的Image Descriptor, 每张图像有且仅有一个Image Descriptor
        :param f: 文件读取时的迭代器
        :return: 包含属性的dict
        """
        res = dict()
        res['image_separator'] = '{:02x}'.format(f.read(1))
        res['image_left_position'] = struct.unpack('H', f.read(2))[0]
        res['image_top_position'] = struct.unpack('H', f.read(2))[0]
        res['image_width'] = struct.unpack('H', f.read(2))[0]
        res['image_height'] = struct.unpack('H', f.read(2))[0]
        packed_fields = f.read(1)
        res['local_color_table_flag'] = read_bits_value_from_bytes(packed_fields, 1, 1)
        res['interlace_flag'] = read_bits_value_from_bytes(packed_fields, 2, 1)
        res['sort_flag'] = read_bits_value_from_bytes(packed_fields, 3, 1)
        res['reversed'] = read_bits_value_from_bytes(packed_fields, 4, 2)
        res['size_of_local_color_table'] = read_bits_value_from_bytes(packed_fields, 6, 3)
        return res

    @staticmethod
    def read_local_color_table(f, image_descriptor_dict):
        """
        读取图像的Local Color Table
        :param f: 文件读取时的迭代器
        :param image_descriptor_dict: 在Local Color Table之前的Image Descriptor的Dict
        :return: 包含颜色bytes的list
        """
        local_color_datas = []
        if image_descriptor_dict['local_color_table_flag'] != 1:
            return local_color_datas
        size = image_descriptor_dict['size_of_local_color_table']
        length = 3 * pow(2, size+1)
        for i in range(length):
            local_color_datas.append(struct.unpack('B', f.read(1))[0])
        return local_color_datas


if __name__ == '__main__':
    decoder = GifDecoder()
    gif_file = "/Users/zz/Workspace/service_gimoji_server/dock_gimojiservice/demo/output/images/1aAZXyY591YSk.gif"
    decoder.read_gif(gif_file)
