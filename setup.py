# coding=utf-8
from setuptools import setup

import pyjoplin

setup(
    name='pyjoplin',
    version=pyjoplin.__version__,
    description=pyjoplin.__doc__.strip(),
    long_description=open('README.md').read(),
    url='https://github.com/jbriales/pyjoplin',
    license=pyjoplin.__license__,
    author=pyjoplin.__author__,
    author_email='jesusbriales@gmail.com',
    packages=['pyjoplin', ],
    install_requires=open('requirements.txt').readlines(),
    entry_points={
        'console_scripts': [
            'pyjoplin = pyjoplin.main:main'
        ],
    },
)
