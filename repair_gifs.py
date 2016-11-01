# -*- coding=utf-8 -*-
"""
修复Gif无法循环播放的问题
1, 89a版本检查如果没有Netscape-Looping-Application-Extension,则加上
2, 87a版本改为89a版本,并且加上Netscape-Looping-Application-Extension
"""
import binascii
from os import listdir
from os.path import isfile, join
from commandr import command, Run
from gif_decode import GifDecoder
from gif_encode import GifEncoder


def check_netscape_looping_application_extension(application_identifier, application_authentication_code,
                                                 application_data):
    """
    检查Application Extension是否为Netscape Looping Application Extension
    :param application_identifier: Application Identifier 8 bytes
    :param application_authentication_code: Application Authentication Code 3 bytes
    :param application_data: Application Data
    :return: 是: True 否: False
    """
    netscape_loop_list = ['21', 'ff', '0b', '4e', '45', '54', '53', '43', '41', '50',
                          '45', '32', '2e', '30', '03', '01', '00', '00', '00']
    start_index = 3  # 从4e开始为Application Identifier
    for byte_ in application_identifier:
        if binascii.hexlify(byte_) != netscape_loop_list[start_index]:
            return False
        start_index += 1
    for byte_ in application_authentication_code:
        if binascii.hexlify(byte_) != netscape_loop_list[start_index]:
            return False
        start_index += 1
    if len(application_data) != 3:
        return False
    start_index += 1
    if binascii.hexlify(application_data[0]) != netscape_loop_list[start_index]:
        return False
    return True


def diagnosis_gif(input_file_path):
    """
    诊断gif是否合法
    :param input_file_path:
    :return: legal: True, illegal: False
    """
    decoder = GifDecoder()
    decoder.read_gif(input_file_path)
    for item_ in decoder.body_data:
        if 'extension_introducer' in item_ and 'application_extension_label' in item_:
            if check_netscape_looping_application_extension(item_['application_identifier'],
                                                                       item_['application_authentication_code'],
                                                                       item_['application_data']):
                return True
    return False


def repair_file(input_file_path, output_file_path):
    """
    修复input文件
    :param input_file_path: input文件路径
    :param output_file_path: output文件路径
    :return: None
    """
    decoder = GifDecoder()
    decoder.read_gif(input_file_path)
    flag = False
    for item_ in decoder.body_data:
        if 'extension_introducer' in item_ and 'application_extension_label' in item_:
            if check_netscape_looping_application_extension(item_['application_identifier'],
                                                                       item_['application_authentication_code'],
                                                                       item_['application_data']):
                flag = True
                break

    with open(output_file_path, 'wb') as f:
        decoder.header['Version'] = ''.join([binascii.unhexlify('38'), binascii.unhexlify('39'),
                                             binascii.unhexlify('61')])  # 强制写为89a版本
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
        if not flag:  # need netscape looping application extension
            print "file {} write netscape looping application extension".format(input_file_path)
            GifEncoder.write_netscape_looping_application_extension(f)
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


@command('find')
def find_not_rotate_gif_under_directory(directory_path):
    """
    查找文件夹下不循环的gif图
    :param directory_path: 文件夹路径
    :return: list of not rotate gif
    """
    files = [f for f in listdir(directory_path) if f.endswith('.gif') and isfile(join(directory_path, f))]
    res, count = [], 0
    for file_ in files:
        count += 1
        print 'check {} gif, name is {}'.format(count, file_)
        try:
            if not diagnosis_gif(join(directory_path, file_)):
                res.append(file_)
        except Exception as e:
            print "********error********** {} ********error**********".format(file_)
            print e.message
    return res


@command('repair')
def repair_file_under_directory(directory_path):
    """
    修复文件夹下的gif文件
    :param directory_path: 文件夹路径
    :return: None
    """
    files = [f for f in listdir(directory_path) if f.endswith('.gif') and isfile(join(directory_path, f))]
    for file_ in files:
        try:
            if not diagnosis_gif(join(directory_path, file_)):
                repair_file(join(directory_path, file_), join(directory_path, 'repair_'+file_))
        except Exception as e:
            print "********error********** {} ********error**********".format(file_)
            print e.message


if __name__ == '__main__':
    Run()