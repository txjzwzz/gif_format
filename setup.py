# -*- coding=utf-8 -*-
import sys
from setuptools import setup, find_packages

version_info = (0, 0, 1)
__version__ = '.'.join(map(str, version_info))

install_requires = [
    'bitarray',
    'commandr',
]

if sys.version_info < (2, 7):
    install_requires += ['argparse==1.2.1']

setup(
    name='gif_analysis',
    author='Zheng Wei',
    author_email='txjzwzz@gmail.com',
    long_descripation=__doc__,
    packages=find_packages('.'),
    packages_dir={'': '.'},
    include_package_data=True,
    packages_data={'': ['*.pig, *.jar']},
    zip_safe=False,
    install_requires=install_requires,
    platforms='any',
)