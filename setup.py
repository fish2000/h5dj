#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by FI$H 2000 on 2012-06-19.
Copyright (c) 2012 Objects In Space And Time, LLC. All rights reserved.

"""

__author__ = 'Alexander Bohn'
__contact__ = 'fish2000@gmail.com'
__version__ = (0, 1, 0)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from setuptools import find_packages

setup(
    name='h5dj',
    version='%s.%s.%s' % __version__,
    description='HDF5 interfaces for Django',
    long_description=""" HDF5 interfaces for Django. """,

    author=__author__,
    author_email=__contact__,
    maintainer=__author__,
    maintainer_email=__contact__,

    license='BSD',
    url='http://github.com/fish2000/h5dj/',
    keywords=[
        'imaging',
        'image analysis',
        'image comparison',
        'image processing',
        'django',
        'numpy', 'arrays',
        'matrix', 'storage'],
    
    packages=find_packages(),
    namespace_packages=['h5dj'],

    install_requires=[
        'numpy', 'h5py', 'django',
        'PIL', 'imread', 'requests'],
    
    tests_require=[
        'nose', 'rednose', 'django-nose'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'],
)
