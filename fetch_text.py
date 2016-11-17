# -*- coding=utf-8 -*-
"""
获取text相关的extension中的数据
"""
from os import listdir
from os.path import isfile, join
from commandr import command, Run
from gif_decode import GifDecoder


@command('fetch_file')
def fetch_text_from_file(filepath):
    """
    从文件中间获取plain text的数据
    :param filepath:
    :return:
    """
    result = set()
    decoder = GifDecoder()
    is_gif = decoder.read_gif(filepath)
    if not is_gif:
        return list(result)
    for item_ in decoder.body_data:
        if 'plain_text_area' in item_:
            result.add(item_['plain_text_area'])
    return list(result)


@command('fetch_directory')
def fetch_text_from_directory(directory_path, output_file_path):
    """
    获取文件夹下gif文件的plain text extension中间的数据,并输出到文件中
    :param directory_path: 待提取plain text的gif所在的文件夹
    :param output_file_path: 结果输出文件
    :return: None
    """
    files = [f for f in listdir(directory_path) if f.endswith('.gif') and isfile(join(directory_path, f))]
    with open(output_file_path, 'w') as f:
        for file_ in files:
            try:
                print file_
                result = fetch_text_from_file(join(directory_path, file_))
                print result
                write_list = [file_] + result
                f.write('|'.join(write_list))
                f.write('\n')
            except Exception as e:
                print e.message
                print "********error********** {} ********error**********".format(file_)


if __name__ == '__main__':
    Run()
