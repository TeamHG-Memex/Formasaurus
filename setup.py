#!/usr/bin/env python
from setuptools import setup
import re
import os


def get_version():
    fn = os.path.join(os.path.dirname(__file__), "formtype", "__init__.py")
    with open(fn) as f:
        return re.findall("__version__ = '([\d\.]+)'", f.read())[0]


setup(
    name='formtype',
    version=get_version(),
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',
    license='MIT license',
    long_description=open('README.rst').read(),
    description="HTML form type detector",
    url='https://github.com/TeamHG-Memex/formtype',
    zip_safe=False,
    packages=['formtype'],
    install_requires=["tqdm", "tldextract"],
    requires=["tqdm", "tldextract", "sklearn", "lxml"],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
