# -*- coding=utf-8 -*-
"""
@author wei.zheng
@date 2016.10.19
"""


class GifDecoder(object):

    def __init__(self):
        pass

    def read_gif(self, filepath):
        """
        读取gif
        :param filepath: gif文件路径
        :return:
        """
        with open(filepath, 'rb') as f:
            self.header = {"Signature": f.read(3), "Version": f.read(3)}
            print self.header


if __name__ == '__main__':
    decoder = GifDecoder()
    gif_file = "/Users/zz/Workspace/service_gimoji_server/dock_gimojiservice/demo/output/images/1aAZXyY591YSk.gif"
    decoder.read_gif(gif_file)
