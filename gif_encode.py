# -*- coding=utf-8 -*-
"""
@author wei.zheng
@date 2016.10.28
"""
import struct
import binascii
from gif_helpers import write_bits_value_to_bytes
from gif_exceptions import ColorTableSizeException, ApplicationIdentifierLengthException, \
                           ApplicationAuthenticationCodeLengthException


class GifEncoder(object):

    def __init__(self):
        pass

    @staticmethod
    def write_header(fw, signature, version):
        """
        写入header
        :param fw: 写文件的迭代器
        :param signature: 3 bytes string for signature
        :param version: 3 bytes string for version
        :return: None
        """
        fw.write(signature)
        fw.write(version)

    @staticmethod
    def write_logical_screen_descriptor(fw, logical_screen_width, logical_screen_height, global_color_table_flag,
                                        color_resolution, sort_flag, size_of_global_color_table,
                                        background_color_index, pixel_aspect_ratio):
        """
        写入logical screen descriptor
        :param fw: 写文件的迭代器
        :param logical_screen_width: integer, width of logical screen width
        :param logical_screen_height: integer, height of logical screen, height
        :param global_color_table_flag: integer, flag of global color table
        :param color_resolution: integer 调色板原色的位数减去1
        :param sort_flag: integer global color table是否排序过
        :param size_of_global_color_table: integer size of global color table
        :param background_color_index: integer background color's index in global color table
        :param pixel_aspect_ratio: integer ratio of pixel height / width, If the
            value of the field is not 0, this approximation of the aspect ratio
            is computed based on the formula: Aspect Ratio = (Pixel Aspect Ratio + 15) / 64
        :return: None
        """
        fw.write(struct.pack('HH', logical_screen_width, logical_screen_height))
        byte_ = write_bits_value_to_bytes([(global_color_table_flag, 1),
                                           (color_resolution, 3),
                                           (sort_flag, 1),
                                           (size_of_global_color_table, 3)])
        fw.write(byte_)
        fw.write(struct.pack('BB', background_color_index, pixel_aspect_ratio))

    @staticmethod
    def write_color_table(fw, size_of_color_table, color_byte_list):
        """
        写入global/local color table, 需要调用前判断是否存在global/local color table
        :param fw: 写文件的迭代器
        :param size_of_color_table: integer size of global/local color table
        :param color_byte_list: list of global/local color bytes
        :return: None
        """
        length = 3 * pow(2, size_of_color_table + 1)
        if length != len(color_byte_list):
            raise ColorTableSizeException(size_of_color_table, len(color_byte_list))
        fw.write(''.join([struct.pack('B', val_) for val_ in color_byte_list]))

    @staticmethod
    def write_image_descriptor(fw, image_left_position, image_top_position, image_width, image_height,
                               local_color_table_flag, interlace_flag, sort_flag, size_of_local_color_table):
        """
        写入image descriptor
        :param fw: 写文件的迭代器
        :param image_left_position: integer, distance to left edge in pixel
        :param image_top_position: integer, distance to top edge in pixel
        :param image_width: integer, width of image
        :param image_height: integer, height of image
        :param local_color_table_flag: integer, flag of local color table
        :param interlace_flag: integer, flag of interlace
        :param sort_flag: integer, flag of sort of local color table
        :param size_of_local_color_table: integer, size of local color table
        :return: None
        """
        # write image separator
        fw.write(binascii.unhexlify('2c'))
        fw.write(struct.pack('HHHH', image_left_position, image_top_position, image_width, image_height))
        byte_ = write_bits_value_to_bytes([(local_color_table_flag, 1),
                                           (interlace_flag, 1),
                                           (sort_flag, 1),
                                           (0, 2),  # reserved
                                           (size_of_local_color_table, 3)])
        fw.write(byte_)

    @classmethod
    def write_table_based_image_data(cls, fw, lzw_minimum_code_size, image_data_byte_list):
        """
        写入Table Based Image Data
        :param fw: 写文件的迭代器
        :param lzw_minimum_code_size: integer, the minimum code size of lzw algorithm
        :param image_data_byte_list: byte list of image data
        :return: None
        """
        fw.write(struct.pack('B', lzw_minimum_code_size))
        fw.write(''.join(cls.generate_bytes_list_sub_block(image_data_byte_list)))

    @staticmethod
    def write_graphic_control_extension(fw, disposal_method, user_input_flag, transparent_color_flag,
                                        delay_time, transparent_color_index):
        """
        写入Graphic Control Extension
        :param fw: 写文件的迭代器
        :param disposal_method: integer, indicates the way in which the graphic is to be treated after being displayed
        :param user_input_flag: integer, indicate whether or not user input is expected
        :param transparent_color_flag: integer, indicates whether a transparency index is given in the transparent index field
        :param delay_time: integer, specifies the number of 1/100 of a second to wait before continue
        :param transparent_color_index: integer, when encountered, the corresponding pixel of the display device is not
                                        modified and processing goes on to the next pixel
        :return: None
        """
        fw.write(binascii.unhexlify('21'))  # extension introducer
        fw.write(binascii.unhexlify('f9'))  # graphic control label
        fw.write(chr(4))  # block size is fixed value 4
        byte_ = write_bits_value_to_bytes([(0, 3),  # reserved
                                           (disposal_method, 3),
                                           (user_input_flag, 1),
                                           (transparent_color_flag, 1)])
        fw.write(byte_)
        fw.write(struct.pack('HBB', delay_time, transparent_color_index, 0))  # last is block terminator

    @classmethod
    def write_comment_extension(cls, fw, comment_byte_list):
        """
        写入 Comment Extension
        :param fw: 写文件的迭代器
        :param comment_byte_list: list of comment byte list
        :return: None
        """
        fw.write(binascii.unhexlify('21'))
        fw.write(binascii.unhexlify('fe'))
        fw.write(''.join(cls.generate_bytes_list_sub_block(comment_byte_list)))

    @classmethod
    def write_plain_text_extension(cls, fw, text_grid_left_position, text_grid_top_position, text_grid_width,
                                   text_grid_height, character_cell_width, character_cell_height,
                                   text_foreground_color_index, text_background_color_index,
                                   plain_text_data_byte_list):
        """
        写入 Plain Text Extension
        :param fw: 写文件的迭代器
        :param text_grid_left_position: integer, distance to left edge of logical screen in pixel
        :param text_grid_top_position: integer, distance to top edge of logical screen in pixel
        :param text_grid_width: integer, width of text grid
        :param text_grid_height: integer, height of text grid
        :param character_cell_width: integer, width of character cell
        :param character_cell_height: integer, height of character cell
        :param text_foreground_color_index: integer, index of foreground color to global color table
        :param text_background_color_index: integer, index of background color to global color table
        :param plain_text_data_byte_list: list of bytes of plain text data
        :return: None
        """
        fw.write(binascii.unhexlify('21'))
        fw.write(binascii.unhexlify('01'))
        fw.write(chr(12))  # size of block is const 12
        fw.write(struct.pack('HHHHBBBB', text_grid_left_position, text_grid_top_position, text_grid_width,
                             text_grid_height, character_cell_width, character_cell_height,
                             text_foreground_color_index, text_background_color_index))
        fw.write(''.join(cls.generate_bytes_list_sub_block(plain_text_data_byte_list)))

    @classmethod
    def write_application_extension(cls, fw, application_identifier_byte_list, application_authentication_code_byte_list,
                                    application_data_byte_list):
        """
        写入Application Extension
        :param fw: 写入文件的迭代器
        :param application_identifier_byte_list: list of application identifier bytes
        :param application_authentication_code_byte_list: list of application authentication code bytes
        :param application_data_byte_list: list of application data bytes
        :return: None
        """
        if len(application_identifier_byte_list) != 8:
            raise ApplicationIdentifierLengthException(len(application_identifier_byte_list))
        if len(application_authentication_code_byte_list) != 3:
            raise ApplicationAuthenticationCodeLengthException(len(application_authentication_code_byte_list))
        fw.write(binascii.unhexlify('21'))
        fw.write(binascii.unhexlify('ff'))
        fw.write(chr(11))  # block size is const 11
        fw.write(''.join(application_identifier_byte_list))
        fw.write(''.join(application_authentication_code_byte_list))
        fw.write(''.join(cls.generate_bytes_list_sub_block(application_data_byte_list)))

    @staticmethod
    def write_trailer(fw):
        """
        write Trailer
        :param fw: 文件写入的迭代器
        :return: None
        """
        fw.write(binascii.unhexlify('3b'))

    @classmethod
    def generate_bytes_list_sub_block(cls, data_byte_list):
        """
        为data byte list生成 sub block, 注意,结果中包含Terminator
        :param data_byte_list: list of data byte
        :return: byte list of sub block, include terminator
        """
        current_start_index, res = 0, []
        # 处理掉大等于255的部分
        while len(data_byte_list) - current_start_index >= 255:
            res.append(chr(255))
            res += data_byte_list[current_start_index: current_start_index+255]
            current_start_index += 255
        if current_start_index < len(data_byte_list):  # 仍有剩余部分
            res.append(chr(len(data_byte_list)-current_start_index))
            res += data_byte_list[current_start_index:]
        res.append(chr(0))
        return res

    @classmethod
    def write_netscape_looping_application_extension(cls, fw):
        """
        写入Netscape Looping Application Extension,让图像循环播放
        :param fw: 文件写入的迭代器
        :return: None
        """
        netscape_loop_list = ['21', 'ff', '0b', '4e', '45', '54', '53', '43', '41', '50',
                              '45', '32', '2e', '30', '03', '01', '00', '00', '00']
        fw.write(''.join([binascii.unhexlify(byte_) for byte_ in netscape_loop_list]))


if __name__ == '__main__':
    from gif_decode import GifDecoder
    decoder = GifDecoder()
    decoder.read_gif('data/rotate.gif')
    with open('data/test_encode.gif', 'wb') as f:
        GifEncoder.write_header(f, decoder.header['Signature'], decoder.header['Version'])
        GifEncoder.write_logical_screen_descriptor(f, decoder.logical_screen_descriptor['logical_screen_width'],
                                                   decoder.logical_screen_descriptor['logical_screen_height'],
                                                   decoder.logical_screen_descriptor['global_color_table_flag'],
                                                   decoder.logical_screen_descriptor['color_resolution'],
                                                   decoder.logical_screen_descriptor['sort_flag'],
                                                   decoder.logical_screen_descriptor['size_of_global_color_table'],
                                                   decoder.logical_screen_descriptor['background_color_index'],
                                                   decoder.logical_screen_descriptor['pixel_aspect_ratio'])
        if decoder.logical_screen_descriptor['global_color_table_flag'] == 1:
            GifEncoder.write_color_table(f, decoder.logical_screen_descriptor['size_of_global_color_table'],
                                         decoder.global_color_table)
        for item_ in decoder.body_data:
            if 'image_descriptor' in item_:  # image data
                GifEncoder.write_image_descriptor(f, item_['image_descriptor']['image_left_position'],
                                                  item_['image_descriptor']['image_top_position'],
                                                  item_['image_descriptor']['image_width'],
                                                  item_['image_descriptor']['image_height'],
                                                  item_['image_descriptor']['local_color_table_flag'],
                                                  item_['image_descriptor']['interlace_flag'],
                                                  item_['image_descriptor']['sort_flag'],
                                                  item_['image_descriptor']['size_of_local_color_table'])
                if item_['image_descriptor']['local_color_table_flag'] == 1:
                    GifEncoder.write_color_table(f, item_['image_descriptor']['size_of_local_color_table'],
                                                 item_['local_color_table'])
                GifEncoder.write_table_based_image_data(f, item_['table_based_image_data']['lzw_minimum_code_size'],
                                                        item_['table_based_image_data']['image_data'])
            elif 'extension_introducer' in item_ and item_['extension_introducer'] == '21' and 'graphic_control_label' in item_:
                GifEncoder.write_graphic_control_extension(f, item_['disposal_method'], item_['user_input_flag'],
                                                           item_['transparent_color_flag'], item_['delay_time'],
                                                           item_['transparent_color_index'])
            elif 'extension_introducer' in item_ and item_['extension_introducer'] == '21' and 'comment_label' in item_:
                GifEncoder.write_comment_extension(f, item_['comment_data'])
            elif 'extension_introducer' in item_ and item_['extension_introducer'] == '21' and 'plain_text_label' in item_:
                GifEncoder.write_plain_text_extension(f, item_['text_grid_left_position'],
                                                      item_['text_grid_top_position'],
                                                      item_['text_grid_width'],
                                                      item_['text_grid_height'],
                                                      item_['character_cell_width'],
                                                      item_['character_cell_height'],
                                                      item_['text_foreground_color_index'],
                                                      item_['text_background_color_index'],
                                                      item_['plain_text_area'])
            elif 'extension_introducer' in item_ and item_['extension_introducer'] == '21' and 'application_extension_label' in item_:
                GifEncoder.write_application_extension(f, item_['application_identifier'],
                                                       item_['application_authentication_code'],
                                                       item_['application_data'])
            else:
                print "Unknown block", item_
        GifEncoder.write_trailer(f)
